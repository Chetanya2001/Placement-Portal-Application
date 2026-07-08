# celery_worker.py
#
# This is the file you point `celery` at on the command line - NOT app.py and
# NOT celery_app.py directly. Reason: importing `app` runs create_app(), which
# calls celery.conf.update(app.config) and installs the Flask-context-aware
# Task class. Only after that has happened is `celery` fully configured.
#
# Run the worker with:
#   celery -A celery_worker.celery worker --loglevel=info
#
# Run beat (the scheduler that fires periodic jobs) with:
#   celery -A celery_worker.celery beat --loglevel=info
#
# In production you'd normally run one combined process with:
#   celery -A celery_worker.celery worker -B --loglevel=info
# (worker + beat together) - fine for small deployments, but a separate
# beat process is safer once you scale to multiple worker machines, since
# beat must only ever run ONE instance at a time (duplicate beats = duplicate
# reminders/reports sent).

from celery.schedules import crontab
from app import create_app
from celery_app import celery

app = create_app()

# --- Periodic schedule (Celery Beat) ---
celery.conf.beat_schedule = {
    "send-interview-reminders-hourly": {
        "task": "tasks.send_interview_reminders",
        "schedule": crontab(minute=0),  # every hour, on the hour
    },
    "generate-monthly-placement-reports": {
        "task": "tasks.generate_monthly_placement_reports",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),  # 1st of month, 6 AM
    },
}
celery.conf.timezone = "Asia/Kolkata"