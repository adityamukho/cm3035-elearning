from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from uniworld.models import Course, CourseMaterial

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

# Add more test classes for other views (CourseUpdateView, CourseDeleteView, CourseMaterialListView, etc.)