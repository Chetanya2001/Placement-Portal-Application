from extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey("students.id"))
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"))
    applied_at = db.Column(db.DateTime, default= datetime.utcnow)
    status = db.Column(db.String(30), default="applied")
    remarks = db.Column(db.Text)
    student = db.relationship("Student", backref="applications")
    drive = db.relationship("PlacementDrive", backref="applications")