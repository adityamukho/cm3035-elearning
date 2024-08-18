from django.contrib.auth.models import User
from django.db import models
from rules import Predicate, is_group_member
from rules.contrib.models import RulesModel

is_course_author = Predicate(lambda user, course: course.user == user)


class Course(RulesModel):
    class Meta:
        rules_permissions = {
            'add': is_group_member('teachers'),
            'change': is_course_author,
            'delete': is_course_author,
        }

    name = models.CharField(max_length=200)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
