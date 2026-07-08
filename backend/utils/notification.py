# utils/notifications.py
#
# Email-only notification helper. Tasks call send_email() instead of talking
# to smtplib directly, so if you ever swap providers (e.g. SendGrid instead
# of raw SMTP) you change it once, here, instead of hunting through every
# task file.

import smtplib
from email.message import EmailMessage

from flask import current_app


def send_email(to, subject, body, attachment_path=None, attachment_name=None):
    """Send a plain-text email, optionally with one file attached (PDF/CSV)."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    msg["To"] = to
    msg.set_content(body)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            file_data = f.read()
        if attachment_path.lower().endswith(".pdf"):
            maintype, subtype = "application", "pdf"
        elif attachment_path.lower().endswith(".csv"):
            maintype, subtype = "text", "csv"
        else:
            maintype, subtype = "application", "octet-stream"
        msg.add_attachment(
            file_data, maintype=maintype, subtype=subtype, filename=attachment_name
        )

    with smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"]) as server:
        server.starttls()
        server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
        server.send_message(msg)