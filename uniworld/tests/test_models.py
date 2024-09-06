from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from uniworld.models import Course, CourseMaterial, Lecture, Assignment, AssignmentQuestion, MCQOption, AssignmentSubmission, QuestionResponse, Feedback

class CourseModelTest(TestCase):
    def setUp(self):
        self.teacher_group = Group.objects.create(name='teachers')
        self.student_group = Group.objects.create(name='students')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.student.groups.add(self.student_group)
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)

    def test_course_creation(self):
        self.assertEqual(self.course.name, 'Test Course')
        self.assertEqual(self.course.description, 'Test Description')
        self.assertEqual(self.course.teacher, self.teacher)

    def test_course_permissions(self):
        # Test view permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('view'), self.course))
        self.assertTrue(self.student.has_perm(Course.get_perm('view'), self.course))

        # Test add permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('add'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('add'), self.course))

        # Test change permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('change'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('change'), self.course))

        # Test delete permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('delete'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('delete'), self.course))

        # Test add_course_material permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('add_course_material'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('add_course_material'), self.course))

        # Test add_feedback permission
        self.assertFalse(self.teacher.has_perm(Course.get_perm('add_feedback'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('add_feedback'), self.course))
        self.course.students.add(self.student)
        self.assertTrue(self.student.has_perm(Course.get_perm('add_feedback'), self.course))

        # Test add_question permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('add_question'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('add_question'), self.course))

        # Test add_option permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('add_option'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('add_option'), self.course))

        # Test enroll_student permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('enroll_student'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('enroll_student'), self.course))

        # Test enroll_self permission
        new_student = User.objects.create_user(username='new_student', password='12345')
        new_student.groups.add(self.student_group)
        self.assertTrue(new_student.has_perm(Course.get_perm('enroll_self'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('enroll_self'), self.course))

class CourseMaterialModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='lecture', sequence=1)

    def test_course_material_creation(self):
        self.assertEqual(self.material.course, self.course)
        self.assertEqual(self.material.title, 'Test Material')
        self.assertEqual(self.material.type, 'lecture')
        self.assertEqual(self.material.sequence, 1)

    def test_course_material_permissions(self):
        # Test view permission
        self.assertTrue(self.teacher.has_perm(CourseMaterial.get_perm('view'), self.material))
        self.assertTrue(self.student.has_perm(CourseMaterial.get_perm('view'), self.material))

        # Test change permission
        self.assertTrue(self.teacher.has_perm(CourseMaterial.get_perm('change'), self.material))
        self.assertFalse(self.student.has_perm(CourseMaterial.get_perm('change'), self.material))

        # Test delete permission
        self.assertTrue(self.teacher.has_perm(CourseMaterial.get_perm('delete'), self.material))
        self.assertFalse(self.student.has_perm(CourseMaterial.get_perm('delete'), self.material))

        # Test view permission for non-enrolled student
        non_enrolled_student = User.objects.create_user(username='non_enrolled', password='12345')
        self.assertFalse(non_enrolled_student.has_perm(CourseMaterial.get_perm('view'), self.material))

# Add more test classes for other models (Lecture, Assignment, AssignmentQuestion, MCQOption, AssignmentSubmission, QuestionResponse, Feedback)