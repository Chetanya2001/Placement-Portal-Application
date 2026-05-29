from extensions import db


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    year = db.Column(db.Integer)
    phone = db.Column(db.Integer)
    skills = db.Column(db.Text)
    resume = db.Column(db.String(200))
    placement_status = db.Column(db.String(20), default="unplaced")

    user = db.relationship("User", backref="students")
