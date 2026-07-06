from flask import Blueprint, jsonify, request
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.company import Company
from models.application import Application
from models.placement_drive import PlacementDrive
from models.interview_schedule import InterviewSchedule

company_bp = Blueprint("company", __name__, url_prefix="/api/company")

def get_current_company():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != "Company":
        return None
    company = Company.query.filter_by(user_id=user.id).first()
    if not company:
        return None
    return company


def blacklist_response():
    """Standard response returned whenever a blacklisted company tries to
    access any protected company endpoint."""
    return jsonify({
        "message": "Your company has been blacklisted. Access denied."
    }), 403


@company_bp.route("/register", methods=["POST"])
def register_company():
    data = request.get_json()

    required_fields = [
        "user_id",
        "company_name",
        "hr_name",
        "hr_email",
        "website",
        "description"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "message": f"{field} is required"
            }), 400

    # Check if user exists
    user = User.query.filter_by(id=data["user_id"]).first()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    # Check if user is a company
    if user.role != "Company":
        return jsonify({
            "message": "Only company users can create a company profile"
        }), 403

    # Check if company profile already exists
    existing_company = Company.query.filter_by(user_id=user.id).first()

    if existing_company:
        return jsonify({
            "message": "Company profile already exists"
        }), 409

    # Create company profile
    company = Company(
        user_id=user.id,
        company_name=data["company_name"],
        hr_name=data["hr_name"],
        hr_email=data["hr_email"],
        website=data["website"],
        description=data["description"],
        approval_status="pending",
        is_blacklisted=False
    )

    db.session.add(company)
    db.session.commit()

    return jsonify({
        "message": "Company profile created successfully. Waiting for admin approval.",
        "company": {
            "id": company.id,
            "company_name": company.company_name,
            "approval_status": company.approval_status
        }
    }), 201


@company_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():

    company = get_current_company()

    if not company:
        return jsonify({"message": "Unauthorized"}), 403

    if company.is_blacklisted:
        return blacklist_response()

    if company.approval_status != "approved":
        return jsonify({"message": "Company not approved"}), 403

    total_jobs = PlacementDrive.query.filter_by(
        company_id=company.id
    ).count()

    total_applications = Application.query.join(
        PlacementDrive
    ).filter(
        PlacementDrive.company_id == company.id
    ).count()

    shortlisted = Application.query.join(
        PlacementDrive
    ).filter(
        PlacementDrive.company_id == company.id,
        Application.status == "shortlisted"
    ).count()

    selected = Application.query.join(
        PlacementDrive
    ).filter(
        PlacementDrive.company_id == company.id,
        Application.status == "selected"
    ).count()

    return jsonify({
        "jobs": total_jobs,
        "applications": total_applications,
        "shortlisted": shortlisted,
        "selected": selected
    }), 200

@company_bp.route("/jobs", methods=["POST"])
@jwt_required()
def create_job():

    company = get_current_company()

    if not company:
        return jsonify({"message":"Unauthorized"}),403

    if company.is_blacklisted:
        return blacklist_response()

    if company.approval_status != "approved":
        return jsonify({"message":"Company not approved"}),403

    data = request.json
    application_deadline = datetime.strptime(
        data["application_deadline"],
        "%Y-%m-%d"
    ).date()

    drive_date = datetime.strptime(
        data["drive_date"],
        "%Y-%m-%d"
    ).date()

    drive = PlacementDrive(
        company_id=company.id,
        job_title=data["job_title"],
        job_description=data["job_description"],
        location=data["location"],
        salary_package=data["salary_package"],
        eligibility_branch=data["eligibility_branch"],
        min_cgpa=data["min_cgpa"],
        eligible_year=data["eligible_year"],
        application_deadline=application_deadline,
        drive_date=drive_date,
        status="pending"
    )

    db.session.add(drive)
    db.session.commit()

    return jsonify({
        "message":"Placement Drive Created"
    }),201

@company_bp.route("/jobs", methods=["GET"])
@jwt_required()
def company_jobs():

    company = get_current_company()

    if not company:
        return jsonify({"message":"Unauthorized"}),403

    if company.is_blacklisted:
        return blacklist_response()

    drives = PlacementDrive.query.filter_by(
        company_id=company.id
    ).all()

    result=[]

    for drive in drives:

        result.append({
            "id":drive.id,
            "job_title":drive.job_title,
            "location":drive.location,
            "salary":drive.salary_package,
            "status":drive.status,
            "deadline":drive.application_deadline
        })

    return jsonify(result),200

@company_bp.route("/jobs/<int:drive_id>/applications", methods=["GET"])
@jwt_required()
def view_applicants(drive_id):

    company = get_current_company()

    if not company:
        return jsonify({"message":"Unauthorized"}),403

    if company.is_blacklisted:
        return blacklist_response()

    drive = PlacementDrive.query.filter_by(
        id=drive_id,
        company_id=company.id
    ).first()

    if not drive:
        return jsonify({"message":"Drive not found"}),404

    result=[]

    for application in drive.applications:

        student = application.student

        result.append({
            "application_id":application.id,
            "student_id":student.id,
            "name":student.user.name,
            "email":student.user.email,
            "branch":student.branch,
            "cgpa":student.cgpa,
            "skills":student.skills,
            "resume":student.resume,
            "status":application.status,
            "remarks":application.remarks
        })

    return jsonify(result),200

@company_bp.route("/applications/<int:id>/shortlist", methods=["PUT"])
@jwt_required()
def shortlist(id):

    company = get_current_company()

    if not company:
        return jsonify({"message":"Unauthorized"}),403

    if company.is_blacklisted:
        return blacklist_response()

    application = Application.query.get(id)

    if not application:
        return jsonify({"message":"Application not found"}),404

    application.status = "shortlisted"

    db.session.commit()

    return jsonify({
        "message":"Applicant Shortlisted"
    }),200

@company_bp.route("/applications/<int:id>/reject", methods=["PUT"])
@jwt_required()
def reject(id):

    company = get_current_company()

    if not company:
        return jsonify({"message":"Unauthorized"}),403

    if company.is_blacklisted:
        return blacklist_response()

    application = Application.query.get(id)

    if not application:
        return jsonify({"message":"Application not found"}),404

    data = request.json

    application.status = "rejected"
    application.remarks = data.get("remarks","")

    db.session.commit()

    return jsonify({
        "message":"Applicant Rejected"
    }),200

@company_bp.route("/applications/<int:id>/select", methods=["PUT"])
@jwt_required()
def select_candidate(id):

    company = get_current_company()

    if not company:
        return jsonify({"message":"Unauthorized"}),403

    if company.is_blacklisted:
        return blacklist_response()

    application = Application.query.get(id)

    if not application:
        return jsonify({"message":"Application not found"}),404

    application.status = "selected"

    application.student.placement_status = "placed"

    db.session.commit()

    return jsonify({
        "message":"Candidate Selected"
    }),200

@company_bp.route("/jobs/<int:id>/status", methods=["PUT"])
@jwt_required()
def update_status(id):

    company = get_current_company()

    if not company:
        return jsonify({"message":"Unauthorized"}),403

    if company.is_blacklisted:
        return blacklist_response()

    drive = PlacementDrive.query.filter_by(
        id=id,
        company_id=company.id
    ).first()

    if not drive:
        return jsonify({"message":"Drive not found"}),404

    data = request.json

    drive.status = data["status"]

    db.session.commit()

    return jsonify({
        "message":"Status Updated"
    }),200

@company_bp.route("/applications/<int:id>/schedule-interview", methods=["POST"])
@jwt_required()
def schedule_interview(id):

    company = get_current_company()

    if not company:
        return jsonify({
            "message": "Unauthorized"
        }), 403

    if company.is_blacklisted:
        return blacklist_response()

    application = Application.query.get(id)

    if not application:
        return jsonify({
            "message": "Application not found"
        }), 404

    # Verify application belongs to this company
    if application.drive.company_id != company.id:
        return jsonify({
            "message": "Unauthorized"
        }), 403

    if application.status != "shortlisted":
        return jsonify({
            "message": "Only shortlisted candidates can be scheduled for interview"
        }), 400

    data = request.get_json()
    interview_datetime = datetime.strptime(
    data["interview_date"],
    "%Y-%m-%dT%H:%M"
)

    interview = InterviewSchedule(
        application_id=application.id,
        interview_date=interview_datetime,
        mode=data["mode"],
        meeting_link=data["meeting_link"]
    )

    db.session.add(interview)

    application.status = "interview scheduled"

    db.session.commit()

    return jsonify({
        "message": "Interview scheduled successfully"
    }), 201

@company_bp.route("/applications/<int:id>/status", methods=["PUT"])
@jwt_required()
def update_application_status(id):

    company = get_current_company()

    if not company:
        return jsonify({
            "message": "Unauthorized"
        }), 403

    if company.is_blacklisted:
        return blacklist_response()

    application = Application.query.get(id)

    if not application:
        return jsonify({
            "message": "Application not found"
        }), 404

    if application.drive.company_id != company.id:
        return jsonify({
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    allowed_status = [
        "shortlisted",
        "selected",
        "rejected"
    ]

    status = data.get("status", "").lower()

    if status not in allowed_status:
        return jsonify({
            "message": "Invalid status"
        }), 400

    application.status = status

    if status == "selected":
        application.student.placement_status = "placed"

    if status == "rejected":
        application.remarks = data.get("remarks", "")

    db.session.commit()

    return jsonify({
        "message": "Application status updated successfully"
    }), 200