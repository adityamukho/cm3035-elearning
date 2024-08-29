from django.contrib.auth.models import User
from django.db import models
from rules import Predicate, is_group_member
from rules.contrib.models import RulesModel

is_course_author = Predicate(lambda user, course: course.teacher == user)


class Course(RulesModel):
    class Meta:
        rules_permissions = {
            'add': is_group_member('teachers'),
            'change': is_course_author,
            'delete': is_course_author,
        }

    name = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='enrolled_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def student_count(self):
        return self.students.count()

    # noinspection PyTypeChecker
    total_students = property(student_count)
