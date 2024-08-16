from django.test import TestCase

import users.tests as user_tests
from .model_factories import *
from .models import *


def global_set_up(instance):
    user_tests.global_set_up(instance)

def global_tear_down():
    Course.objects.all().delete()

    user_tests.global_tear_down()
    CourseFactory.reset_sequence(0)

class CourseTestCase(TestCase):
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

    def test_TeacherCanCreateCourse(self):
        teacher = self.user_teacher

        self.assertTrue(teacher.has_perm(Course.get_perm('add')))
        try:
            course = CourseFactory.create(user=teacher, name='test course')
            self.assertIsInstance(course, Course)
            self.assertEqual(course.name, 'test course')
        except Exception as e:
            self.fail(e)

    def test_StudentCannotCreateCourse(self):
        student = self.user_student

        self.assertFalse(student.has_perm(Course.get_perm('add')))
