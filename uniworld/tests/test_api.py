from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from uniworld.models import Course, CourseMaterial, Assignment, AssignmentQuestion, MCQOption, AssignmentSubmission, QuestionResponse, Feedback, Lecture
from uniworld.serializers import (
    CourseSerializer, CourseMaterialSerializer, AssignmentQuestionSerializer,
    MCQOptionSerializer, AssignmentSubmissionSerializer, QuestionResponseSerializer,
    FeedbackSerializer, LectureSerializer, AssignmentSerializer
)

User = get_user_model()

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

class AssignmentQuestionAPITest(APITestCase):
    def setUp(self):
        self.teacher_group = Group.objects.create(name='teachers')
        self.student_group = Group.objects.create(name='students')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.student.groups.add(self.student_group)
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')
        self.question = AssignmentQuestion.objects.create(assignment=self.assignment, question_text='Test Question', question_type='MCQ', marks=5)

    def test_assignment_question_list(self):
        url = reverse('assignmentquestion-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assignment_question_create(self):
        url = reverse('assignmentquestion-list')
        data = {
            'assignment': self.assignment.material.id,
            'question_text': 'New API Question',
            'question_type': 'MCQ',
            'marks': 5
        }

        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class MCQOptionAPITest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')
        self.question = AssignmentQuestion.objects.create(assignment=self.assignment, question_text='Test Question', question_type='MCQ', marks=5)
        self.option = MCQOption.objects.create(question=self.question, option_text='Test Option', is_correct=True)

    def test_mcq_option_list(self):
        url = reverse('mcqoption-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        options = MCQOption.objects.all()
        serializer = MCQOptionSerializer(options, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mcq_option_create(self):
        url = reverse('mcqoption-list')
        data = {
            'question': self.question.id,
            'option_text': 'New API Option',
            'is_correct': False
        }
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AssignmentSubmissionAPITest(APITestCase):
    def setUp(self):
        self.teacher_group = Group.objects.create(name='teachers')
        self.student_group = Group.objects.create(name='students')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.student.groups.add(self.student_group)
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')
        self.submission = AssignmentSubmission.objects.create(assignment=self.assignment, student=self.student)

    def test_assignment_submission_list(self):
        url = reverse('assignmentsubmission-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        submissions = AssignmentSubmission.objects.all()
        serializer = AssignmentSubmissionSerializer(submissions, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assignment_submission_create(self):
        url = reverse('assignmentsubmission-list')
        data = {
            'assignment': self.assignment.material.id,
            'student': self.student.id
        }
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class QuestionResponseAPITest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')
        self.question = AssignmentQuestion.objects.create(assignment=self.assignment, question_text='Test Question', question_type='MCQ', marks=5)
        self.submission = AssignmentSubmission.objects.create(assignment=self.assignment, student=self.student)
        self.response = QuestionResponse.objects.create(submission=self.submission, question=self.question, response_text='Test Response')

    def test_question_response_list(self):
        url = reverse('questionresponse-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        responses = QuestionResponse.objects.all()
        serializer = QuestionResponseSerializer(responses, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_response_create(self):
        url = reverse('questionresponse-list')
        data = {
            'submission': self.submission.id,
            'question': self.question.id,
            'response_text': 'New API Response'
        }
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class FeedbackAPITest(APITestCase):
    def setUp(self):
        self.teacher_group = Group.objects.create(name='teachers')
        self.student_group = Group.objects.create(name='students')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.student.groups.add(self.student_group)
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.feedback = Feedback.objects.create(course=self.course, user=self.student, rating=4, comment='Good course')

    def test_feedback_list(self):
        url = reverse('feedback-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        feedbacks = Feedback.objects.all()
        serializer = FeedbackSerializer(feedbacks, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_feedback_create(self):
        url = reverse('feedback-list')
        data = {
            'course': self.course.id,
            'user': self.student.id,
            'rating': 5,
            'comment': 'Excellent course'
        }
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class LectureAPITest(APITestCase):
    def setUp(self):
        self.teacher_group = Group.objects.create(name='teachers')
        self.student_group = Group.objects.create(name='students')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.student.groups.add(self.student_group)
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='lecture', sequence=1)
        self.lecture = Lecture.objects.create(material=self.material, content='Test Content')

    def test_lecture_list(self):
        url = reverse('lecture-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        lectures = Lecture.objects.all()
        serializer = LectureSerializer(lectures, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lecture_create(self):
        url = reverse('lecture-list')
        material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='lecture', sequence=2)
        data = {
            'material': material.id,
            'content': 'New API Lecture Content'
        }
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AssignmentAPITest(APITestCase):
    def setUp(self):
        self.teacher_group = Group.objects.create(name='teachers')
        self.student_group = Group.objects.create(name='students')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher.groups.add(self.teacher_group)
        self.student = User.objects.create_user(username='student', password='12345')
        self.student.groups.add(self.student_group)
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.course.students.add(self.student)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')

    def test_assignment_list(self):
        url = reverse('assignment-list')
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        assignments = Assignment.objects.all()
        serializer = AssignmentSerializer(assignments, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assignment_create(self):
        url = reverse('assignment-list')
        material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=2)
        data = {
            'material': material.id,
            'due_date': '2024-01-31 23:59:59 +00:00'
        }
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

