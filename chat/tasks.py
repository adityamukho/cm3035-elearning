from celery import shared_task
from django.contrib.auth import get_user_model

User = get_user_model()

from django.core.mail import send_mail


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