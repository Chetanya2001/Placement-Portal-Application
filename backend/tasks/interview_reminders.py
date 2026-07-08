# tasks/interview_reminders.py
#
# ASSUMPTIONS ABOUT YOUR MODELS (adjust names/fields to match your real schema):
#   - Interview: id, student_id, company_id, scheduled_at (DateTime), reminder_sent (Boolean)
#   - Interview.student -> relationship to Student (has .email)
#   - Interview.company -> relationship to Company (has .name)
#
# If your Interview model doesn't have `reminder_sent` yet, add it via a
# migration - without it this job would re-send the same reminder every hour
# until the interview time passes.

from datetime import datetime, timedelta

from celery.utils.log import get_task_logger

from celery_app import celery
from extensions import db
from models.interview import Interview  # adjust import path to your actual model location
from utils.notifications import send_email

logger = get_task_logger(__name__)

# How far ahead to look for upcoming interviews each time this task runs.
REMINDER_WINDOW_HOURS = 24


@celery.task(name="tasks.send_interview_reminders")
def send_interview_reminders():
    """
    Runs on a schedule (see celery_worker.py's beat_schedule - hourly by default).
    Finds interviews happening within the next REMINDER_WINDOW_HOURS that haven't
    had a reminder sent yet, and emails the student.
    """
    window_start = datetime.utcnow()
    window_end = window_start + timedelta(hours=REMINDER_WINDOW_HOURS)

    upcoming = Interview.query.filter(
        Interview.scheduled_at.between(window_start, window_end),
        Interview.reminder_sent.is_(False),
    ).all()

    sent_count = 0
    failed_count = 0

    for interview in upcoming:
        student = interview.student
        company = interview.company

        message = (
            f"Reminder: You have an interview with {company.name} scheduled on "
            f"{interview.scheduled_at.strftime('%d %b %Y, %I:%M %p')}."
        )

        try:
            if getattr(student, "email", None):
                send_email(
                    to=student.email,
                    subject="Upcoming Interview Reminder",
                    body=message,
                )

            interview.reminder_sent = True
            db.session.commit()
            sent_count += 1

        except Exception as exc:
            # One failed notification shouldn't crash the whole batch - log it,
            # roll back just that row, and keep going with the rest.
            logger.error("Failed to send reminder for interview %s: %s", interview.id, exc)
            db.session.rollback()
            failed_count += 1

    logger.info("Interview reminders: %s sent, %s failed", sent_count, failed_count)
    return {"sent": sent_count, "failed": failed_count}