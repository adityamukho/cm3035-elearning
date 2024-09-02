from django.contrib.auth.models import User
from django.db import models
from rules import Predicate, is_group_member
from rules.contrib.models import RulesModel
from chat.models import Room

is_course_author = Predicate(lambda user, course: course.teacher == user)


class Course(RulesModel):
    class Meta:
        rules_permissions = {
            'view': lambda user, course: user.is_authenticated and user not in course.blocked_students.all(),
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

class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.course} - {self.rating}"
