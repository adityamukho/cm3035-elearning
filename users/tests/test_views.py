import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse

@pytest.fixture
def students_group(db):
    group, created = Group.objects.get_or_create(name='students')
    return group

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')


@pytest.mark.django_db
def test_register_view(client, students_group, user):
    url = reverse('register')
    response = client.post(url, {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': '364TB011222',
        'password2': '364TB011222',
    })

    assert response.status_code == 302
    assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_profile_view(client, user):
    client.login(username='testuser', password='12345')

    url = reverse('profile')
    response = client.get(url, follow=True)
    print(response)

    assert response.status_code == 200
    assert 'user_form' in response.context
    assert 'profile_form' in response.context
