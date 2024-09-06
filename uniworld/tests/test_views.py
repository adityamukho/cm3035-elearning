from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from uniworld.models import Course, CourseMaterial, Assignment, AssignmentQuestion, AssignmentSubmission, QuestionResponse, MCQOption, Feedback

User = get_user_model()

class CourseListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_group = Group.objects.create(name='teachers')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)

    def test_course_list_view(self):
        self.client.login(username='teacher', password='12345')
        response = self.client.get(reverse('courses'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')

        self.client.login(username='student', password='12345')
        response = self.client.get(reverse('courses'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')

class CourseDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)

    def test_course_detail_view(self):
        self.client.login(username='teacher', password='12345')
        response = self.client.get(reverse('course-detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')
        self.assertContains(response, 'Test Description')

        self.client.login(username='student', password='12345')
        response = self.client.get(reverse('course-detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')
        self.assertContains(response, 'Test Description')

class CourseCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_group = Group.objects.create(name='teachers')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')

    def test_course_create_view(self):
        self.client.login(username='teacher', password='12345')
        response = self.client.post(reverse('course-create'), {
            'name': 'New Course',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Course.objects.filter(name='New Course').exists())

        self.client.login(username='student', password='12345')
        response = self.client.post(reverse('course-create'), {
            'name': 'Student Course',
            'description': 'Student Description'
        })
        self.assertEqual(response.status_code, 403)  # Forbidden for students
        self.assertFalse(Course.objects.filter(name='Student Course').exists())

class AssignmentQuestionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')
        self.question = AssignmentQuestion.objects.create(assignment=self.assignment, question_text='Test Question', question_type='MCQ', marks=5)

    def test_assignment_question_create_view(self):
        self.client.login(username='teacher', password='12345')
        response = self.client.post(reverse('add-assignment-question', kwargs={'assignment_id': self.assignment.material.id}), {
            'question_text': 'New Question',
            'question_type': 'ESSAY',
            'marks': 10
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(AssignmentQuestion.objects.filter(question_text='New Question').exists())

        self.client.login(username='student', password='12345')
        response = self.client.post(reverse('add-assignment-question', kwargs={'assignment_id': self.assignment.material.id}), {
            'question_text': 'Student Question',
            'question_type': 'MCQ',
            'marks': 5
        })
        self.assertEqual(response.status_code, 403)  # Forbidden for students
        self.assertFalse(AssignmentQuestion.objects.filter(question_text='Student Question').exists())

class AssignmentSubmissionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')

    def test_assignment_submission_create_view(self):
        self.client.login(username='student', password='12345')
        response = self.client.post(reverse('submit-assignment', kwargs={'assignment_id': self.assignment.material.id}), {})
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(AssignmentSubmission.objects.filter(student=self.student, assignment=self.assignment).exists())

        self.client.login(username='teacher', password='12345')
        response = self.client.post(reverse('submit-assignment', kwargs={'assignment_id': self.assignment.material.id}), {})
        self.assertEqual(response.status_code, 403)  # Forbidden for teachers
        self.assertFalse(AssignmentSubmission.objects.filter(student=self.teacher, assignment=self.assignment).exists())

class FeedbackViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_group = Group.objects.create(name='teachers')
        self.student_group = Group.objects.create(name='students')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.student.groups.add(self.student_group)
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)

    def test_feedback_create_view(self):
        self.client.login(username='student', password='12345')
        response = self.client.post(reverse('course-feedback', kwargs={'course_id': self.course.id}), {
            'rating': 4,
            'comment': 'Great course!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Feedback.objects.filter(user=self.student, course=self.course).exists())

        self.client.login(username='teacher', password='12345')
        response = self.client.post(reverse('course-feedback', kwargs={'course_id': self.course.id}), {
            'rating': 5,
            'comment': 'Teacher feedback'
        })
        self.assertEqual(response.status_code, 403)  # Forbidden for teachers
        self.assertFalse(Feedback.objects.filter(user=self.teacher, course=self.course).exists())

# Add more test classes for other views (CourseUpdateView, CourseDeleteView, CourseMaterialListView, etc.)