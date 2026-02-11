import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.settings import settings


class EmailService:

    @staticmethod
    def send_email(to_email: str, subject: str, html_body: str):
        msg = MIMEMultipart()
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_EMAIL, to_email, msg.as_string())

    # ---------------- EMAIL TYPES ---------------- #

    @staticmethod
    def send_email_verification(to_email: str, token: str):
        link = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"

        html = f"""
        <h2>Confirm your email</h2>
        <p>Click the button below to verify your account:</p>
        <a href="{link}">Verify email</a>
        <br><br>
        If the button doesn't work — open this link manually:<br>
        {link}
        """

        EmailService.send_email(
            to_email,
            "Verify your email",
            html
        )

    @staticmethod
    def send_password_reset(to_email: str, token: str):
        link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"

        html = f"""
        <h2>Password reset request</h2>
        <p>You requested a password reset.</p>
        <p>Click the button below to proceed:</p>
        <a href="{link}">Reset password</a>
        <br><br>
        If the button doesn't work — open this link manually:<br>
        {link}
        """

        EmailService.send_email(
            to_email,
            "Reset your password",
            html
        )
