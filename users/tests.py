from django.test import TestCase
from .model_factories import *
from .models import Profile

# Common setup function used by all test suites.
def global_set_up(instance):
    instance.group_teachers = GroupFactory.create(name='teachers')
    instance.group_students = GroupFactory.create(name='students')

    instance.user_teacher = UserFactory.create(username='teacher')
    instance.user_teacher.groups.add(instance.group_teachers)

    instance.user_student = UserFactory.create(username='student')
    instance.user_student.groups.add(instance.group_students)

    instance.profile_teacher = instance.user_teacher.profile
    instance.profile_student = instance.user_student.profile


# Common teardown function used by all test suites.
def global_tear_down():
    Profile.objects.all().delete()
    User.objects.all().delete()
    Group.objects.all().delete()

    UserFactory.reset_sequence(0)
    GroupFactory.reset_sequence(0)

class ProfileModelTests(TestCase):
    group_teachers = None
    group_students = None
    user_teacher = None
    user_student = None
    profile_teacher = None
    profile_student = None

    def setUp(self):
        global_set_up(self)

    def tearDown(self):
        global_tear_down()

    def test_ProfileHasUser(self):
        profile = self.profile_teacher

        self.assertIsInstance(profile, Profile)
        self.assertIsInstance(profile.user, User)

    def test_ProfileHasGroup(self):
        profile = self.profile_student
        self.assertIsInstance(profile, Profile)
        self.assertIsInstance(profile.user, User)

        groups = profile.user.groups.all()
        self.assertIsNotNone(groups)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0], self.group_students)