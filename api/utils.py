from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import threading

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Utils:
    @staticmethod
    def send_email(data):
        subject = data['email_subject']
        to_email = [data['to_email']]
        text_content = data['email_body']
        html_content = data['email_body']

        email = EmailMultiAlternatives(subject, text_content, to=to_email)
        email.attach_alternative(html_content, "text/html")

        EmailThread(email).start()
