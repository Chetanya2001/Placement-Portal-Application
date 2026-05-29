from extensions import db

class InterviewSchedule(db.Model):
    __tablename__ = "interview_schedules"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"))
    interview_date = db.Column(db.DateTime)
    mode = db.Column(db.String(30))
    meeting_link = db.Column(db.String(300))
    status = db.Column(db.String(20), default="schedule")
    applications = db.relationship("Application", backref="interview_schedules")

