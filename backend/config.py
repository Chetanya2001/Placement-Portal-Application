import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "placement.db")
    JWT_SECRET_KEY = "23f3001153"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    