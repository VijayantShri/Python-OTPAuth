from django.core.mail import send_mail
from random import randint
from django.conf import settings
from accounts.models import User
from datetime import datetime

def send_otp_via_email(email):
    subject = f'Your account verification email'
    otp = randint(1000, 9999)
    message = f'Your account verification otp is {otp}'
    email_from = settings.EMAIL_HOST
    send_mail(subject=subject, message=message, from_email=email_from, recipient_list=[email])
    user_obj = User.objects.get(email=email)
    user_obj.otp = otp
    user_obj.otp_created_at = datetime.now()
    user_obj.save()