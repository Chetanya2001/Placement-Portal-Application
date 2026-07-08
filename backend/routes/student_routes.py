from datetime import datetime, date
import io
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.company import Company
from models.placement_drive import PlacementDrive
from models.student import Student
from models.application import Application
from models.interview_schedule import InterviewSchedule
from tasks.csv_export import export_student_history

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from utils.cache_utils import cache_response, delete_pattern


student_bp = Blueprint("student", __name__, url_prefix="/api/student")


def get_current_student():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != "Student":
        return None
    student = Student.query.filter_by(user_id=user.id).first()
    if not student:
        return None
    return student





# ---------- Profile registration (separate from auth) ----------

@student_bp.route("/register", methods=["POST"])
def register_student():
    data = request.get_json()

    required_fields = ["user_id"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "message": f"{field} is required"
            }), 400

    user = User.query.filter_by(id=data["user_id"]).first()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if user.role != "Student":
        return jsonify({
            "message": "Only student users can create a student profile"
        }), 403

    existing_student = Student.query.filter_by(user_id=user.id).first()

    if existing_student:
        return jsonify({
            "message": "Student profile already exists"
        }), 409

    student = Student(
        user_id=user.id,
        branch=data.get("branch"),
        cgpa=data.get("cgpa"),
        year=data.get("year"),
        phone=data.get("phone"),
        skills=data.get("skills"),
        resume=data.get("resume"),
        placement_status="unplaced"
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student profile created successfully.",
        "student": {
            "id": student.id,
            "name": user.name,
            "branch": student.branch
        }
    }), 201


@student_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    return jsonify({
        "id": student.id,
        "name": student.user.name,
        "email": student.user.email,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "year": student.year,
        "phone": student.phone,
        "skills": student.skills,
        "resume": student.resume,
        "placement_status": student.placement_status
    }), 200


@student_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()

    updatable_fields = ["branch", "cgpa", "year", "phone", "skills", "resume"]

    for field in updatable_fields:
        if field in data:
            setattr(student, field, data[field])

    if "name" in data:
        student.user.name = data["name"]

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully"
    }), 200


# ---------- View and search job postings ----------

@student_bp.route("/jobs", methods=["GET"])
@jwt_required()
@cache_response("jobs:list", ttl=180, query_params=["company", "position", "skill"])
def browse_jobs():
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    print("Total drives:", PlacementDrive.query.count())
    query = PlacementDrive.query.join(Company).filter(
        PlacementDrive.status == "approved",
        Company.is_blacklisted == False
    )

    company_name = request.args.get("company")
    position = request.args.get("position")
    skill = request.args.get("skill")

    if company_name:
        query = query.filter(Company.company_name.ilike(f"%{company_name}%"))

    if position:
        query = query.filter(PlacementDrive.job_title.ilike(f"%{position}%"))

    if skill:
        query = query.filter(
            db.or_(
                PlacementDrive.job_description.ilike(f"%{skill}%"),
                PlacementDrive.eligibility_branch.ilike(f"%{skill}%")
            )
        )
        print("After skill filter:", query.count())

    drives = query.order_by(PlacementDrive.application_deadline.asc()).all()

    result = []

    for drive in drives:
        result.append({
            "id": drive.id,
            "job_title": drive.job_title,
            "company_name": drive.company.company_name,
            "location": drive.location,
            "salary": drive.salary_package,
            "eligibility_branch": drive.eligibility_branch,
            "min_cgpa": drive.min_cgpa,
            "eligible_year": drive.eligible_year,
            "deadline": drive.application_deadline,
            "drive_date": drive.drive_date
        })

    return jsonify(result), 200


@student_bp.route("/jobs/<int:drive_id>", methods=["GET"])
@jwt_required()
@cache_response("jobs:detail", ttl=300)
def job_detail(drive_id):
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    drive = PlacementDrive.query.filter_by(id=drive_id).first()

    if not drive:
        return jsonify({"message": "Job not found"}), 404

    return jsonify({
        "id": drive.id,
        "job_title": drive.job_title,
        "job_description": drive.job_description,
        "company_name": drive.company.company_name,
        "location": drive.location,
        "salary": drive.salary_package,
        "eligibility_branch": drive.eligibility_branch,
        "min_cgpa": drive.min_cgpa,
        "eligible_year": drive.eligible_year,
        "deadline": drive.application_deadline,
        "drive_date": drive.drive_date,
        "status": drive.status
    }), 200


# ---------- Apply for jobs and track application status ----------

@student_bp.route("/jobs/<int:drive_id>/apply", methods=["POST"])
@jwt_required()
def apply_job(drive_id):
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    drive = PlacementDrive.query.filter_by(id=drive_id).first()

    if not drive:
        return jsonify({"message": "Job not found"}), 404

    if drive.status != "approved" and drive.status != "active":
        return jsonify({"message": "This drive is not open for applications"}), 400

    if drive.application_deadline and drive.application_deadline < date.today():
        return jsonify({"message": "Application deadline has passed"}), 400

    if student.placement_status == "placed":
        return jsonify({"message": "You are already placed and cannot apply"}), 400

    if drive.min_cgpa and (student.cgpa is None or student.cgpa < drive.min_cgpa):
        return jsonify({"message": "You do not meet the minimum CGPA requirement"}), 400

    if drive.eligibility_branch and student.branch:
        eligible_branches = [b.strip().lower() for b in drive.eligibility_branch.split(",")]
        if student.branch.strip().lower() not in eligible_branches:
            return jsonify({"message": "Your branch is not eligible for this drive"}), 400

    if drive.eligible_year and student.year and student.year != drive.eligible_year:
        return jsonify({"message": "You are not eligible based on year"}), 400

    existing_application = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive.id
    ).first()

    if existing_application:
        return jsonify({"message": "You have already applied to this job"}), 409

    application = Application(
        student_id=student.id,
        drive_id=drive.id,
        status="applied"
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        "message": "Application submitted successfully",
        "application_id": application.id
    }), 201


# ---------- View applied jobs with detailed status ----------

@student_bp.route("/applications", methods=["GET"])
@jwt_required()
def my_applications():
    student = get_current_student()
    print(student)
    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    status_filter = request.args.get("status")

    query = Application.query.filter_by(student_id=student.id)

    if status_filter:
        query = query.filter(Application.status == status_filter.lower())

    applications = query.order_by(Application.applied_at.desc()).all()

    result = []

    for application in applications:
        result.append({
            "application_id": application.id,
            "job_title": application.drive.job_title,
            "company_name": application.drive.company.company_name,
            "location": application.drive.location,
            "salary": application.drive.salary_package,
            "applied_at": application.applied_at,
            "status": application.status,
            "remarks": application.remarks
        })

    return jsonify(result), 200


@student_bp.route("/applications/<int:id>", methods=["GET"])
@jwt_required()
def application_detail(id):
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    application = Application.query.filter_by(
        id=id,
        student_id=student.id
    ).first()

    if not application:
        return jsonify({"message": "Application not found"}), 404

    drive = application.drive

    return jsonify({
        "application_id": application.id,
        "job_title": drive.job_title,
        "job_description": drive.job_description,
        "company_name": drive.company.company_name,
        "location": drive.location,
        "salary": drive.salary_package,
        "applied_at": application.applied_at,
        "status": application.status,
        "remarks": application.remarks
    }), 200


# ---------- View interview schedules and feedback ----------

@student_bp.route("/interviews", methods=["GET"])
@jwt_required()
def my_interviews():
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    interviews = InterviewSchedule.query.join(Application).filter(
        Application.student_id == student.id
    ).order_by(InterviewSchedule.interview_date.asc()).all()

    result = []

    for interview in interviews:
        application = Application.query.get(interview.application_id)
        drive = application.drive

        result.append({
            "interview_id": interview.id,
            "application_id": application.id,
            "job_title": drive.job_title,
            "company_name": drive.company.company_name,
            "interview_date": interview.interview_date,
            "mode": interview.mode,
            "meeting_link": interview.meeting_link,
            "status": interview.status,
            "application_status": application.status,
            "feedback": application.remarks
        })

    return jsonify(result), 200


@student_bp.route("/interviews/<int:id>", methods=["GET"])
@jwt_required()
def interview_detail(id):
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    interview = InterviewSchedule.query.get(id)

    if not interview:
        return jsonify({"message": "Interview not found"}), 404

    application = Application.query.get(interview.application_id)

    if not application or application.student_id != student.id:
        return jsonify({"message": "Unauthorized"}), 403

    drive = application.drive

    return jsonify({
        "interview_id": interview.id,
        "job_title": drive.job_title,
        "company_name": drive.company.company_name,
        "interview_date": interview.interview_date,
        "mode": interview.mode,
        "meeting_link": interview.meeting_link,
        "status": interview.status,
        "application_status": application.status,
        "feedback": application.remarks
    }), 200


# ---------- Download offer letter / placement confirmation (PDF) ----------

@student_bp.route("/applications/<int:id>/offer-letter", methods=["GET"])
@jwt_required()
def offer_letter(id):
    student = get_current_student()

    if not student:
        return jsonify({"message": "Unauthorized"}), 403

    application = Application.query.filter_by(
        id=id,
        student_id=student.id
    ).first()

    if not application:
        return jsonify({"message": "Application not found"}), 404

    if application.status != "selected":
        return jsonify({
            "message": "Offer letter is only available for selected applications"
        }), 400

    drive = application.drive
    company = drive.company

    pdf_buffer = _build_offer_letter_pdf(student, application, drive, company)

    filename = f"offer_letter_{company.company_name}_{application.id}.pdf".replace(" ", "_")

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


def _build_offer_letter_pdf(student, application, drive, company):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "OfferTitle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "OfferSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20
    )

    body_style = ParagraphStyle(
        "OfferBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=12
    )

    story = []

    story.append(Paragraph(company.company_name, title_style))
    story.append(Paragraph("Placement Confirmation Letter", subtitle_style))

    today_str = datetime.utcnow().strftime("%B %d, %Y")
    story.append(Paragraph(f"Date: {today_str}", body_style))

    story.append(Paragraph(
        f"Dear {student.user.name},",
        body_style
    ))

    intro = (
        f"We are pleased to confirm your selection for the position of "
        f"<b>{drive.job_title}</b> at <b>{company.company_name}</b>, "
        f"following the placement drive conducted on "
        f"{drive.drive_date.strftime('%B %d, %Y') if drive.drive_date else 'N/A'}. "
        f"This letter serves as an official confirmation of your placement."
    )
    story.append(Paragraph(intro, body_style))

    story.append(Spacer(1, 12))

    details_data = [
        ["Candidate Name", student.user.name],
        ["Branch", student.branch or "N/A"],
        ["Position", drive.job_title],
        ["Location", drive.location or "N/A"],
        ["Annual Package", f"{drive.salary_package:,.2f}" if drive.salary_package else "N/A"],
        ["Application Status", application.status.title()],
    ]

    details_table = Table(details_data, colWidths=[2.2 * inch, 3.5 * inch])
    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(details_table)
    story.append(Spacer(1, 20))

    closing = (
        "This confirmation is generated based on the placement records on file "
        "and is intended for academic and informational purposes. For an official "
        "offer letter with terms of employment, please refer to the documentation "
        "shared directly by the company's HR team."
    )
    story.append(Paragraph(closing, body_style))

    story.append(Spacer(1, 30))
    story.append(Paragraph(f"HR Contact: {company.hr_name}", body_style))
    story.append(Paragraph(f"Email: {company.hr_email}", body_style))

    doc.build(story)

    buffer.seek(0)
    return buffer

@student_bp.route("/export", methods=["POST"])
@jwt_required()
def trigger_student_export():
    student_id = get_jwt_identity()
    task = export_student_history.delay(student_id)
    # 202 Accepted = "request understood, work is happening in the background"
    return jsonify({"message": "Export started", "task_id": task.id}), 202
 
 
@student_bp.route("/export/status/<task_id>", methods=["GET"])
@jwt_required()
def student_export_status(task_id):
    task = export_student_history.AsyncResult(task_id)
    return jsonify({
        "state": task.state,          # PENDING / STARTED / SUCCESS / FAILURE
        "result": task.result if task.ready() else None,
    })