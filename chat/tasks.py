from django.contrib.auth.models import User
from django.core.mail import send_mail
from celery import shared_task
from openai import APIError

from chat.models import Message


@shared_task
def send_api_error_mail(error_message):
    admin = User.objects.get(username='admin')

    send_mail(
        subject='An exception occurred',
        message=error_message,
        from_email='system@uniworld.example',
        recipient_list=[admin.email],
        fail_silently=False,
    )