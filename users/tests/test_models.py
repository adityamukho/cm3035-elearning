from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from users.models import Profile
from rules.contrib.models import RulesModel

User = get_user_model()

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

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

    def test_profile_permissions(self):
        # Test view permission
        self.assertTrue(self.user.has_perm(Profile.get_perm('view'), self.profile))
        self.assertTrue(self.other_user.has_perm(Profile.get_perm('view'), self.profile))

        # Test change permission
        self.assertTrue(self.user.has_perm(Profile.get_perm('change'), self.profile))
        self.assertFalse(self.other_user.has_perm(Profile.get_perm('change'), self.profile))

        # Test delete permission
        self.assertFalse(self.user.has_perm(Profile.get_perm('delete'), self.profile))
        self.assertFalse(self.other_user.has_perm(Profile.get_perm('delete'), self.profile))