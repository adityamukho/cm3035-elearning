import pytest
from django.contrib.auth.models import User

from users.models import Profile


@pytest.mark.django_db
def test_profile_creation():
    user = User.objects.create_user(username='testuser', password='12345')
    profile = Profile.objects.get(user=user)

    assert profile.user == user
    assert profile.avatar.name == 'avatar.jpg'  # Check default avatar


@pytest.mark.django_db
def test_profile_str_method():
    user = User.objects.create_user(username='testuser', password='12345')
    profile = Profile.objects.get(user=user)

    assert str(profile) == 'testuser Profile'
