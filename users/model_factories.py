import factory

from django.contrib.auth.models import User, Group


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User