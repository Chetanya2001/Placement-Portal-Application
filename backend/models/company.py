from extensions import db

class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    company_name = db.Column(db.String(200))
    hr_name = db.Column(db.String(100))
    hr_email = db.Column(db.String(100))
    website = db.Column(db.String(200))
    description = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default="pending")
    is_blacklisted = db.Column(db.Boolean, default=False)
    user = db.relationship("User", backref="company")