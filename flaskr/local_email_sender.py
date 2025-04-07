import smtplib

from flask import current_app
from flaskr.email_interface import EmailInterface


class LocalSmtpEmailInterface(EmailInterface):

    def send_email(self, to_email, reset_link):
        sender_email = "support@skillr.com"
        # only used when having auth on
        #sender_password = "your-password"

        smtp_server = current_app.config['SMTP_SERVER']
        smtp_port = current_app.config['SMTP_PORT']

        subject = "Password Reset Request"
        body = f"Click the link to reset your password: {reset_link}"

        message = f"Subject: {subject}\n\n{body}"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # aiosmtpd supports starttls but it's disabled by default
            # you can enable it but then you need a certificate which is out of scope for this project
            # server.starttls()

            # aiosmtp doesn't support SMTP AUTH
            # server.login(sender_email, sender_password)
            server.ehlo()
            server.sendmail(sender_email, to_email, message)
