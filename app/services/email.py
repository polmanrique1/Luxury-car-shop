import os
import ssl
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

def send_mail(to_email: str, car: object):
    email_provider = os.getenv("EMAIL")
    password_smtp = os.getenv("PASSWORD")

    if not email_provider or not password_smtp:
        raise RuntimeError("Email credentials not configured")

    subject = "Purchase"
    body = f"you have purchsased: {car.model}"

    em = EmailMessage()
    em["From"] = email_provider
    em["To"] = to_email
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_provider, password_smtp)
        smtp.send_message(em)
