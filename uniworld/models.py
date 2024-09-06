from django.contrib.auth.models import User
from django.db import models
from rules import Predicate, is_group_member, always_deny, is_authenticated
from rules.contrib.models import RulesModel
from chat.models import Room
from mimetypes import guess_type

is_course_author = Predicate(lambda user, course: course.teacher == user)
not_blocked = Predicate(lambda user, course: user not in course.blocked_students.all())
is_enrolled = Predicate(lambda user, course: user in course.students.all())
is_enrolled_feedback = Predicate(lambda user, feedback: user in feedback.course.students.all())
is_enrolled_material = Predicate(lambda user, material: user in material.course.students.all())
is_course_author_material = Predicate(lambda user, material: user == material.course.teacher)
is_course_author_question = Predicate(lambda user, question: user == question.assignment.material.course.teacher)
is_enrolled_submission = Predicate(lambda user, submission: user in submission.assignment.material.course.students.all())
is_enrolled_question = Predicate(lambda user, question: user in question.assignment.material.course.students.all())
is_course_author_mcq_option = Predicate(lambda user, option: user == option.question.assignment.material.course.teacher)
is_enrolled_mcq_option = Predicate(lambda user, option: user in option.question.assignment.material.course.students.all())
is_course_author_submission = Predicate(lambda user, submission: user == submission.assignment.material.course.teacher)
is_enrolled_response = Predicate(lambda user, response: user in response.submission.assignment.material.course.students.all())
is_course_author_response = Predicate(lambda user, response: user == response.question.assignment.material.course.teacher)
is_submission_author = Predicate(lambda user, submission: user == submission.student)
is_response_author = Predicate(lambda user, response: user == response.submission.student)

class Course(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_authenticated & not_blocked,
            'add': is_group_member('teachers'),
            'change': is_course_author,
            'delete': is_course_author,
        }

    name = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    blocked_students = models.ManyToManyField(User, related_name='blocked_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chat_room = models.OneToOneField(Room, on_delete=models.CASCADE, null=True, related_name='course')

    def __str__(self):
        return self.name

    def student_count(self):
        return self.students.count()

    # noinspection PyTypeChecker
    total_students = property(student_count)

    def enroll_student(self, user):
        if user not in self.students.all():
            self.students.add(user)
            return True
        return False

    def average_rating(self):
        feedbacks = self.feedback.all()
        if feedbacks.exists():
            return round(feedbacks.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    average_rating = property(average_rating)

class Feedback(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_authenticated,
            'add': is_enrolled_feedback,
            'change': always_deny,
            'delete': always_deny,
        }
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.course} - {self.rating}"

class CourseMaterial(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_enrolled_material,
            'add': is_course_author_material,
            'change': is_course_author_material,
            'delete': is_course_author_material,
        }

    COURSE_MATERIAL_TYPES = [
        ('lecture', 'Lecture'),
        ('assignment', 'Assignment'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=COURSE_MATERIAL_TYPES)
    sequence = models.IntegerField()

    class Meta:
        ordering = ['sequence']

class Lecture(models.Model):
    material = models.OneToOneField(CourseMaterial, on_delete=models.CASCADE, primary_key=True)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    document = models.FileField(upload_to='lectures/', null=True, blank=True)
    document_mime_type = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.document:
            mime_type, _ = guess_type(self.document.url)
            self.document_mime_type = mime_type
        super().save(*args, **kwargs)

class Assignment(models.Model):
    material = models.OneToOneField(CourseMaterial, on_delete=models.CASCADE, primary_key=True)
    due_date = models.DateTimeField()

    def total_marks(self):
        return self.questions.aggregate(total=models.Sum('marks'))['total'] or 0

    def __str__(self):
        return f"Assignment for {self.material.title}"

class AssignmentQuestion(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_course_author_question | is_enrolled_question,
            'add': is_course_author_question,
            'change': is_course_author_question,
            'delete': is_course_author_question,
        }

    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('ESSAY', 'Essay'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=5, choices=QUESTION_TYPES)
    marks = models.PositiveIntegerField()

    def __str__(self):
        return f"Question for {self.assignment.material.title}"

class MCQOption(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_course_author_mcq_option | is_enrolled_mcq_option,
            'add': is_course_author_mcq_option,
            'change': is_course_author_mcq_option,
            'delete': is_course_author_mcq_option,
        }

    question = models.ForeignKey(AssignmentQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

class AssignmentSubmission(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_course_author_submission | is_submission_author,
            'add': is_enrolled_submission,
            'change': is_course_author_submission,
            'delete': always_deny,
        }

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    total_score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def calculate_total_score(self):
        total_score = 0
        responses = self.responses.all()
        for response in responses:
            if response.question.question_type == 'MCQ':
                if response.selected_option and response.selected_option.is_correct:
                    total_score += response.question.marks
            elif response.question.question_type == 'ESSAY':
                if response.score is not None:
                    total_score += response.score
        self.total_score = total_score
        self.save()

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.material.title}"

class QuestionResponse(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_course_author_response | is_response_author,
            'add': is_enrolled_response,
            'change': is_course_author_response,
            'delete': always_deny,
        }

    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(AssignmentQuestion, on_delete=models.CASCADE)
    response_text = models.TextField(blank=True, null=True)
    selected_option = models.ForeignKey(MCQOption, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Response to question {self.question.id} in {self.submission}"
