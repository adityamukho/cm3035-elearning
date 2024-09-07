from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from uniworld.models import Course, CourseMaterial, Assignment, AssignmentQuestion, MCQOption, AssignmentSubmission, QuestionResponse, Feedback

User = get_user_model()

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

        # Test leave_course permission
        self.assertTrue(self.student.has_perm(Course.get_perm('leave_course'), self.course))
        self.assertFalse(self.teacher.has_perm(Course.get_perm('leave_course'), self.course))

        # Test remove_student permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('remove_student'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('remove_student'), self.course))

        # Test block_student permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('block_student'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('block_student'), self.course))

        # Test unblock_student permission
        self.assertTrue(self.teacher.has_perm(Course.get_perm('unblock_student'), self.course))
        self.assertFalse(self.student.has_perm(Course.get_perm('unblock_student'), self.course))

        # Test add_submission permission
        self.assertFalse(self.teacher.has_perm(Course.get_perm('add_submission'), self.course))
        self.assertTrue(self.student.has_perm(Course.get_perm('add_submission'), self.course))

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
        self.assertTrue(self.teacher.has_perm(CourseMaterial.get_perm('view'), self.material))
        self.assertTrue(self.student.has_perm(CourseMaterial.get_perm('view'), self.material))
        self.assertTrue(self.teacher.has_perm(CourseMaterial.get_perm('change'), self.material))
        self.assertFalse(self.student.has_perm(CourseMaterial.get_perm('change'), self.material))
        self.assertTrue(self.teacher.has_perm(CourseMaterial.get_perm('delete'), self.material))
        self.assertFalse(self.student.has_perm(CourseMaterial.get_perm('delete'), self.material))

        # Test view permission for non-enrolled student
        non_enrolled_student = User.objects.create_user(username='non_enrolled', password='12345')
        self.assertFalse(non_enrolled_student.has_perm(CourseMaterial.get_perm('view'), self.material))

class AssignmentQuestionModelTest(TestCase):
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
        self.question = AssignmentQuestion.objects.create(assignment=self.assignment, question_text='Test Question', question_type='MCQ', marks=5)

    def test_assignment_question_creation(self):
        self.assertEqual(self.question.assignment, self.assignment)
        self.assertEqual(self.question.question_text, 'Test Question')
        self.assertEqual(self.question.question_type, 'MCQ')
        self.assertEqual(self.question.marks, 5)

    def test_assignment_question_permissions(self):
        self.assertTrue(self.teacher.has_perm(AssignmentQuestion.get_perm('view'), self.question))
        self.assertTrue(self.student.has_perm(AssignmentQuestion.get_perm('view'), self.question))
        self.assertTrue(self.teacher.has_perm(AssignmentQuestion.get_perm('change'), self.question))
        self.assertFalse(self.student.has_perm(AssignmentQuestion.get_perm('change'), self.question))
        self.assertTrue(self.teacher.has_perm(AssignmentQuestion.get_perm('delete'), self.question))
        self.assertFalse(self.student.has_perm(AssignmentQuestion.get_perm('delete'), self.question))
        self.assertTrue(self.teacher.has_perm(AssignmentQuestion.get_perm('add_option'), self.question))
        self.assertFalse(self.student.has_perm(AssignmentQuestion.get_perm('add_option'), self.question))
        self.assertFalse(self.teacher.has_perm(AssignmentQuestion.get_perm('add_response'), self.question))
        self.assertTrue(self.student.has_perm(AssignmentQuestion.get_perm('add_response'), self.question))

class MCQOptionModelTest(TestCase):
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
        self.question = AssignmentQuestion.objects.create(assignment=self.assignment, question_text='Test Question', question_type='MCQ', marks=5)
        self.option = MCQOption.objects.create(question=self.question, option_text='Test Option', is_correct=True)

    def test_mcq_option_creation(self):
        self.assertEqual(self.option.question, self.question)
        self.assertEqual(self.option.option_text, 'Test Option')
        self.assertTrue(self.option.is_correct)

    def test_mcq_option_permissions(self):
        self.assertTrue(self.teacher.has_perm(MCQOption.get_perm('view'), self.option))
        self.assertTrue(self.student.has_perm(MCQOption.get_perm('view'), self.option))
        self.assertTrue(self.teacher.has_perm(MCQOption.get_perm('change'), self.option))
        self.assertFalse(self.student.has_perm(MCQOption.get_perm('change'), self.option))
        self.assertTrue(self.teacher.has_perm(MCQOption.get_perm('delete'), self.option))
        self.assertFalse(self.student.has_perm(MCQOption.get_perm('delete'), self.option))

class AssignmentSubmissionModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')
        self.submission = AssignmentSubmission.objects.create(assignment=self.assignment, student=self.student)

    def test_assignment_submission_creation(self):
        self.assertEqual(self.submission.assignment, self.assignment)
        self.assertEqual(self.submission.student, self.student)

    def test_assignment_submission_permissions(self):
        self.assertTrue(self.teacher.has_perm(AssignmentSubmission.get_perm('view'), self.submission))
        self.assertTrue(self.student.has_perm(AssignmentSubmission.get_perm('view'), self.submission))
        self.assertTrue(self.teacher.has_perm(AssignmentSubmission.get_perm('change'), self.submission))
        self.assertFalse(self.student.has_perm(AssignmentSubmission.get_perm('change'), self.submission))
        self.assertFalse(self.teacher.has_perm(AssignmentSubmission.get_perm('delete'), self.submission))
        self.assertFalse(self.student.has_perm(AssignmentSubmission.get_perm('delete'), self.submission))

class QuestionResponseModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.material = CourseMaterial.objects.create(course=self.course, title='Test Material', type='assignment', sequence=1)
        self.assignment = Assignment.objects.create(material=self.material, due_date='2023-12-31 23:59:59 +00:00')
        self.question = AssignmentQuestion.objects.create(assignment=self.assignment, question_text='Test Question', question_type='MCQ', marks=5)
        self.submission = AssignmentSubmission.objects.create(assignment=self.assignment, student=self.student)
        self.response = QuestionResponse.objects.create(submission=self.submission, question=self.question, response_text='Test Response')

    def test_question_response_creation(self):
        self.assertEqual(self.response.submission, self.submission)
        self.assertEqual(self.response.question, self.question)
        self.assertEqual(self.response.response_text, 'Test Response')

    def test_question_response_permissions(self):
        self.assertTrue(self.teacher.has_perm(QuestionResponse.get_perm('view'), self.response))
        self.assertTrue(self.student.has_perm(QuestionResponse.get_perm('view'), self.response))
        self.assertTrue(self.teacher.has_perm(QuestionResponse.get_perm('change'), self.response))
        self.assertFalse(self.student.has_perm(QuestionResponse.get_perm('change'), self.response))
        self.assertFalse(self.teacher.has_perm(QuestionResponse.get_perm('delete'), self.response))
        self.assertFalse(self.student.has_perm(QuestionResponse.get_perm('delete'), self.response))

class FeedbackModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.student = User.objects.create_user(username='student', password='12345')
        self.course = Course.objects.create(name='Test Course', description='Test Description', teacher=self.teacher)
        self.feedback = Feedback.objects.create(course=self.course, user=self.student, rating=4, comment='Good course')

    def test_feedback_creation(self):
        self.assertEqual(self.feedback.course, self.course)
        self.assertEqual(self.feedback.user, self.student)
        self.assertEqual(self.feedback.rating, 4)
        self.assertEqual(self.feedback.comment, 'Good course')

    def test_feedback_permissions(self):
        self.assertTrue(self.teacher.has_perm(Feedback.get_perm('view'), self.feedback))
        self.assertTrue(self.student.has_perm(Feedback.get_perm('view'), self.feedback))
        self.assertFalse(self.teacher.has_perm(Feedback.get_perm('change'), self.feedback))
        self.assertTrue(self.student.has_perm(Feedback.get_perm('change'), self.feedback))
        self.assertFalse(self.teacher.has_perm(Feedback.get_perm('delete'), self.feedback))
        self.assertTrue(self.student.has_perm(Feedback.get_perm('delete'), self.feedback))