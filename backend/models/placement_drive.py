from extensions import db

class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    job_title = db.Column(db.String(200))
    job_description = db.Column(db.Text)
    location = db.Column(db.String(100))
    salary_package = db.Column(db.Float)
    eligibility_branch = db.Column(db.String(200))
    min_cgpa = db.Column(db.Float)
    eligible_year = db.Column(db.Integer)
    application_deadline = db.Column(db.Date)
    drive_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="pending")
    company = db.relationship("Company", backref = "placement_drives")