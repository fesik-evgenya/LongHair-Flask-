import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_mail(to_email: str, subject: str, message: str) -> bool:
    try:
        load_dotenv()
        msg = MIMEMultipart()
        msg['From'] = os.getenv('FROM')
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP_SSL(os.getenv('HOST'), int(os.getenv('PORT'))) as server:
            server.login(os.getenv('FROM'), os.getenv('PASSWORD'))
            server.send_message(msg)
            logger.info(f"Письмо отправлено на {to_email}")
            return True
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}", exc_info=True)
        return False