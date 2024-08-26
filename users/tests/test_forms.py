import pytest
from django.contrib.auth.models import User

from users.forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from users.models import Profile


@pytest.mark.django_db
def test_register_form_valid():
    form_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'password123',
        'password2': 'password123',
    }
    form = RegisterForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_user_update_form():
    user = User.objects.create_user(username='testuser', email='oldemail@example.com', password='12345')
    form_data = {'email': 'newemail@example.com'}
    form = UserUpdateForm(data=form_data, instance=user)

    assert form.is_valid()
    updated_user = form.save()
    assert updated_user.email == 'newemail@example.com'


@pytest.mark.django_db
def test_profile_update_form():
    user = User.objects.create_user(username='testuser', password='12345')
    profile = Profile.objects.create(user=user)
    form_data = {'avatar': 'path/to/new/avatar.jpg'}  # Mock file upload if needed
    form = ProfileUpdateForm(data=form_data, instance=profile)

    assert form.is_valid()
    updated_profile = form.save()
    assert updated_profile.avatar.name == 'path/to/new/avatar.jpg'  # Adjust based on actual file handling
