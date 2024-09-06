from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Profile

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.avatar.name, 'avatar.jpg')

    def test_profile_str_representation(self):
        self.assertEqual(str(self.profile), f'{self.user.username} Profile')

    def test_profile_auto_creation(self):
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        self.assertTrue(Profile.objects.filter(user=new_user).exists())