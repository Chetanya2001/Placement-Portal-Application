# config.py
#
# Your original settings (SQLALCHEMY_DATABASE_URI, JWT_*) kept exactly as you
# had them. Added: Redis/Celery URLs, SMTP mail settings, Twilio SMS settings.
# Secrets (mail password, Twilio token) are pulled from environment variables
# so you're not committing real credentials to source control - set them in
# a .env file or your shell before running the app/worker.

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Your existing settings, unchanged ---
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "placement.db")
    JWT_SECRET_KEY = "23f3001153"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # --- Redis / Celery ---
    # Redis is both the broker (queue that hands jobs from Flask to workers)
    # and the result backend (stores task results so you can poll status,
    # e.g. for the CSV export endpoint).
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # --- Email (SMTP via smtplib) - used by all three background jobs ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "PlacementPortal@placement.com")
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/1")
    CACHE_DEFAULT_TTL = int(os.environ.get("CACHE_DEFAULT_TTL", 300))

