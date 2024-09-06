from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from uniworld.models import Course, CourseMaterial
from uniworld.serializers import CourseSerializer, CourseMaterialSerializer

class CourseAPITest(APITestCase):
    def setUp(self):
        self.teacher_group = Group.objects.create(name='teachers')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)

    def test_course_list(self):
        url = reverse('course-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_create(self):
        url = reverse('course-list')
        data = {'name': 'New API Course', 'description': 'API Description', 'teacher': self.teacher.id}
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CourseMaterialAPITest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='lecture', sequence=1)

    def test_course_material_list(self):
        url = reverse('coursematerial-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        materials = CourseMaterial.objects.all()
        serializer = CourseMaterialSerializer(materials, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_material_create(self):
        url = reverse('coursematerial-list')
        data = {'course': self.course.id, 'title': 'New API Material', 'type': 'lecture', 'sequence': 2}
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# Add more test classes for other API endpoints (LectureViewSet, AssignmentViewSet, etc.)