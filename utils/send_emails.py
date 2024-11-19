from django.core import mail
from django.conf import settings

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_custom_email(to, subject, html_content) -> bool:
    subject, from_email = subject, settings.EMAIL_HOST_USER
    body = MIMEText(html_content, _subtype='html')
    email = MIMEMultipart(_subtype='related')
    email['From'] = from_email
    email['Subject'] = subject
    email['To'] = ",".join([to])
    email.attach(body)

    try:
        server = smtplib.SMTP_SSL(settings.EMAIL_HOST)
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        text = email.as_bytes()
        server.sendmail(from_email, email['To'].split(","), text)
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False
