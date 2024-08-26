import pytest
from django.contrib.auth.models import User
from django.core import mail

from chat.tasks import send_api_error_mail


@pytest.mark.django_db
def test_send_api_error_mail():
    admin = User.objects.create_user(username='admin', email='admin@example.com', password='12345')
    send_api_error_mail("Test error message")
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'An exception occurred'
    assert mail.outbox[0].body == 'Test error message'
    assert mail.outbox[0].to == [admin.email]
