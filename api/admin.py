from django.contrib import admin

from .models import Course, Profile, Student, Teacher

admin.site.register(Course)
admin.site.register(Profile)
admin.site.register(Student)
admin.site.register(Teacher)
