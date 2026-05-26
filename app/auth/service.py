from flask_mail import Message
from flask import Flask,current_app
import logging
from app.extension import mail
def send_email(link,email):
    msg = Message(
                    subject="Verify your email",
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[email],
                    body=f"Click to verify your email: {link}"
                )
    current_app.logger.info("📧 SENDING MAIL...")
    mail.send(msg)