import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
def test_register_view(client):
    url = reverse('register')
    response = client.post(url, {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'password123',
        'password2': 'password123',
    })

    assert response.status_code == 302  # Redirect after successful registration
    assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_profile_view(client):
    client.login(username='testuser', password='12345')

    url = reverse('profile')
    response = client.get(url)

    assert response.status_code == 200
    assert 'user_form' in response.context
    assert 'profile_form' in response.context
