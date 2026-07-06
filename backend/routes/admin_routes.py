from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db

from models.student import Student
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.user import User

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


def get_current_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or user.role != "admin":
        return None

    return user


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    return jsonify({
        "students": total_students,
        "companies": total_companies,
        "placement_drives": total_drives,
        "applications": total_applications
    }), 200


@admin_bp.route("/companies", methods=["GET"])
@jwt_required()
def get_companies():

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    companies = Company.query.all()

    result = []

    for company in companies:
        result.append({
            "id": company.id,
            "company_name": company.company_name,
            "hr_name": company.hr_name,
            "hr_email": company.hr_email,
            "approval_status": company.approval_status,
            "blacklisted": company.is_blacklisted
        })

    return jsonify(result), 200


@admin_bp.route("/companies/<int:id>/approve", methods=["PUT"])
@jwt_required()
def approve_company(id):

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only admin can access"}), 403

    company = Company.query.get(id)

    if not company:
        return jsonify({"message": "Company Not Found"}), 404

    company.approval_status = "approved"

    db.session.commit()

    return jsonify({"message": "Company approved"}), 200


@admin_bp.route("/companies/<int:id>/reject", methods=["PUT"])
@jwt_required()
def reject_company(id):

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only admin can access"}), 403

    company = Company.query.get(id)

    if not company:
        return jsonify({"message": "Company Not Found"}), 404

    company.approval_status = "rejected"

    db.session.commit()

    return jsonify({"message": "Company rejected"}), 200


@admin_bp.route("/companies/<int:id>/blacklisted", methods=["PUT"])
@jwt_required()
def blacklist_company(id):

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only admin can access"}), 403

    company = Company.query.get(id)

    if not company:
        return jsonify({"message": "Company Not Found"}), 404

    company.is_blacklisted = True

    db.session.commit()

    return jsonify({"message": "Company Blacklisted"}), 200


@admin_bp.route("/companies/search", methods=["GET"])
@jwt_required()
def search_companies():

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    name = request.args.get("name", "")

    companies = Company.query.filter(
        Company.company_name.ilike(f"%{name}%")
    ).all()

    result = []

    for company in companies:
        result.append({
            "id": company.id,
            "name": company.company_name,
            "approval_status": company.approval_status
        })

    return jsonify(result), 200


@admin_bp.route("/students/search", methods=["GET"])
@jwt_required()
def search_students():

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    name = request.args.get("name", "")

    students = Student.query.join(User).filter(
        User.name.ilike(f"%{name}%")
    ).all()

    result = []

    for student in students:
        result.append({
            "id": student.id,
            "name": student.user.name,
            "email": student.user.email,
            "branch": student.branch,
            "cgpa": student.cgpa
        })

    return jsonify(result), 200


@admin_bp.route("/students/<int:id>/deactivate", methods=["PUT"])
@jwt_required()
def student_deactivate(id):

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    student = Student.query.get(id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    student.user.is_active = False

    db.session.commit()

    return jsonify({
        "message": "Student deactivate successfully"
    }), 200


@admin_bp.route("/drives", methods=["GET"])
@jwt_required()
def get_drives():

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    drives = PlacementDrive.query.all()

    result = []

    for drive in drives:
        result.append({
            "id": drive.id,
            "job_title": drive.job_title,
            "company": drive.company.company_name,
            "status": drive.status
        })

    return jsonify(result), 200


@admin_bp.route("/drives/<int:id>/approve", methods=["PUT"])
@jwt_required()
def approve_drive(id):

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    drive = PlacementDrive.query.get(id)

    if not drive:
        return jsonify({
            "message": "Placement drive not found"
        }), 404

    drive.status = "approved"

    db.session.commit()

    return jsonify({
        "message": "Placement drive approved"
    }), 200


@admin_bp.route("/drives/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_drive(id):

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    drive = PlacementDrive.query.get(id)

    if not drive:
        return jsonify({
            "message": "Placement drive not found"
        }), 404

    db.session.delete(drive)
    db.session.commit()

    return jsonify({
        "message": "Placement drive deleted"
    }), 200


@admin_bp.route("/applications", methods=["GET"])
@jwt_required()
def get_applications():

    user = get_current_admin()

    if not user:
        return jsonify({"message": "Only Admin Can Access"}), 403

    applications = Application.query.all()

    result = []

    for application in applications:
        result.append({
            "id": application.id,
            "student_id": application.student.id,
            "student": application.student.user.name,
            "job_title": application.drive.job_title,
            "status": application.status
        })

    return jsonify(result), 200

@admin_bp.route("/profile/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student_profile(student_id):
    admin = get_current_admin()

    if not admin:
        return jsonify({"message": "Unauthorized"}), 403

    student = Student.query.get(student_id)

    if not student:
        return jsonify({"message": "Student not found"}), 404

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

@admin_bp.route("/applications/<int:id>", methods=["GET"])
@jwt_required()
def get_application_detail(id):

    admin = get_current_admin()

    if not admin:
        return jsonify({"message": "Only Admin Can Access"}), 403

    application = Application.query.get(id)

    if not application:
        return jsonify({"message": "Application not found"}), 404

    student = application.student
    drive = application.drive

    return jsonify({
        "application_id": application.id,
        "student": student.user.name,
        "email": student.user.email,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "job_title": drive.job_title,
        "company": drive.company.company_name,
        "location": drive.location,
        "salary": drive.salary_package,
        "status": application.status,
        "remarks": application.remarks,
        "applied_at": application.applied_at
    }), 200