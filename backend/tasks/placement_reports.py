# tasks/placement_reports.py
#
# ASSUMPTIONS ABOUT YOUR MODELS (adjust to your real schema):
#   - Company: id, name, email
#   - Application: id, student_id, company_id, status, applied_at (DateTime)
#     (status assumed to be one of e.g. "applied", "shortlisted", "rejected",
#     "selected" - adjust the values checked below to match your real ones)
#   - Placement: id, student_id, company_id, package (Numeric/Float), placed_at (DateTime)
#
# Produces BOTH an HTML file and a PDF file per company per month (the
# milestone asks for "HTML / PDF"), then emails the PDF as an attachment.
#
# PDF generation uses xhtml2pdf (pure Python, no system dependencies like
# wkhtmltopdf/Cairo) - good enough for tabular reports like this. If you
# later want pixel-perfect CSS support, swap in WeasyPrint instead; the
# render_template() call stays the same, only the HTML->PDF step changes.

import os
from calendar import monthrange
from collections import Counter
from datetime import datetime
from io import BytesIO

from celery.utils.log import get_task_logger
from flask import render_template
from xhtml2pdf import pisa

from celery_app import celery
from models.company import Company
from models.application import Application
from models.placement_drive import PlacementDrive
from utils.notification import send_email

logger = get_task_logger(__name__)

REPORTS_DIR = "generated_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def _build_company_stats(company, period_start, period_end):
    """Pull every number the report template needs for one company/month."""
    applications = Application.query.filter(
        Application.company_id == company.id,
        Application.applied_at.between(period_start, period_end),
    ).all()

    placements = PlacementDrive.query.filter(
        PlacementDrive.company_id == company.id,
        PlacementDrive.placed_at.between(period_start, period_end),
    ).all()

    total_applications = len(applications)
    total_placements = len(placements)
    conversion_rate = round((total_placements / total_applications) * 100, 2) if total_applications else 0

    # Breakdown of application statuses, e.g. {"applied": 12, "shortlisted": 4, "rejected": 6, "selected": 2}
    # Adjust the status strings here if your Application.status values differ.
    status_counts = Counter(app.status for app in applications)

    packages = [p.package for p in placements if getattr(p, "package", None) is not None]
    average_package = round(sum(packages) / len(packages), 2) if packages else 0
    highest_package = max(packages) if packages else 0

    return {
        "company": company,
        "period": period_start.strftime("%B %Y"),
        "total_applications": total_applications,
        "total_placements": total_placements,
        "conversion_rate": conversion_rate,
        "status_counts": dict(status_counts),
        "average_package": average_package,
        "highest_package": highest_package,
        "applications": applications,
        "placements": placements,
    }


@celery.task(name="tasks.generate_monthly_placement_reports")
def generate_monthly_placement_reports(month=None, year=None):
    """
    Runs on the 1st of every month (see celery_worker.py's beat_schedule).
    For each company, builds an HTML report from that month's applications
    and placements, saves the HTML, renders it to PDF, saves that too, and
    emails the PDF to the company as an attachment.

    Pass explicit `month`/`year` (e.g. from the Celery shell or an admin
    route) to backfill/regenerate a specific month's report on demand.
    """
    now = datetime.utcnow()
    month = month or now.month
    year = year or now.year
    _, last_day = monthrange(year, month)
    period_start = datetime(year, month, 1)
    period_end = datetime(year, month, last_day, 23, 59, 59)

    companies = Company.query.all()
    generated_files = []

    for company in companies:
        stats = _build_company_stats(company, period_start, period_end)

        html = render_template("reports/placement_report.html", **stats)

        base_name = f"placement_report_{company.id}_{year}_{month:02d}"
        html_filename = f"{base_name}.html"
        pdf_filename = f"{base_name}.pdf"
        html_filepath = os.path.join(REPORTS_DIR, html_filename)
        pdf_filepath = os.path.join(REPORTS_DIR, pdf_filename)

        # Save the HTML version (as required by the milestone).
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html)

        # Convert the same HTML to PDF and save that too.
        pdf_buffer = BytesIO()
        pisa.CreatePDF(src=html, dest=pdf_buffer)
        pdf_buffer.seek(0)
        with open(pdf_filepath, "wb") as f:
            f.write(pdf_buffer.read())

        if getattr(company, "email", None):
            send_email(
                to=company.email,
                subject=f"Placement Report - {stats['period']}",
                body=(
                    f"Please find attached your placement report for {stats['period']}.\n\n"
                    f"Applications: {stats['total_applications']}\n"
                    f"Placements: {stats['total_placements']}\n"
                    f"Conversion rate: {stats['conversion_rate']}%"
                ),
                attachment_path=pdf_filepath,
                attachment_name=pdf_filename,
            )

        generated_files.append({"html": html_filename, "pdf": pdf_filename})

    logger.info("Generated %s monthly placement reports for %s/%s", len(generated_files), month, year)
    return {"reports_generated": generated_files}