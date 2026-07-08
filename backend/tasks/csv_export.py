# tasks/csv_export.py
#
# These tasks are NOT on a schedule - they're triggered on demand from a
# route (see routes_additions.py) when a student/company clicks "Export".
# That's the "User-triggered" part of the milestone: the HTTP request kicks
# off the job and returns immediately with a task_id; the actual CSV building
# + email happens in the background so the request doesn't hang.

import csv
import os
from datetime import datetime

from celery.utils.log import get_task_logger

from celery_app import celery
from models.student import Student
from models.company import Company
from models.application import Application
from models.placement_drive import PlacementDrive
from utils.notification import send_email

logger = get_task_logger(__name__)

EXPORTS_DIR = "generated_exports"
os.makedirs(EXPORTS_DIR, exist_ok=True)


@celery.task(name="tasks.export_student_history", bind=True)
def export_student_history(self, student_id):
    student = Student.query.get(student_id)
    if not student:
        return {"status": "error", "message": "Student not found"}

    applications = Application.query.filter_by(student_id=student_id).all()
    placements = PlacementDrive.query.filter_by(student_id=student_id).all()

    filename = f"student_{student_id}_export_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join(EXPORTS_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Company", "Status", "Date"])
        for app in applications:
            writer.writerow(["Application", app.company.name, app.status, app.applied_at])
        for p in placements:
            writer.writerow(["Placement", p.company.name, "Placed", p.placed_at])

    if getattr(student, "email", None):
        send_email(
            to=student.email,
            subject="Your export is ready",
            body="Your application/placement history export has completed. See attached CSV.",
            attachment_path=filepath,
            attachment_name=filename,
        )

    logger.info("Student export complete: %s", filename)
    return {"status": "completed", "file": filename}


@celery.task(name="tasks.export_company_history", bind=True)
def export_company_history(self, company_id):
    company = Company.query.get(company_id)
    if not company:
        return {"status": "error", "message": "Company not found"}

    applications = Application.query.filter_by(company_id=company_id).all()
    placements = PlacementDrive.query.filter_by(company_id=company_id).all()

    filename = f"company_{company_id}_export_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join(EXPORTS_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Student", "Status", "Date"])
        for app in applications:
            writer.writerow(["Application", app.student.name, app.status, app.applied_at])
        for p in placements:
            writer.writerow(["Placement", p.student.name, "Placed", p.placed_at])

    if getattr(company, "email", None):
        send_email(
            to=company.email,
            subject="Your export is ready",
            body="Your application/placement history export has completed. See attached CSV.",
            attachment_path=filepath,
            attachment_name=filename,
        )

    logger.info("Company export complete: %s", filename)
    return {"status": "completed", "file": filename}