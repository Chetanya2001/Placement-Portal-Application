from celery import Celery

celery = Celery(
    "placement_portal",
    include=[
        "tasks.interview_reminders",
        "tasks.placement_reports",
        "tasks.csv_export",
    ],
)

celery.conf.update(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0",
    timezone="Asia/Kolkata",
)