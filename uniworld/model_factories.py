import factory

from .models import Course

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course