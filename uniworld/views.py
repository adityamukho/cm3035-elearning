from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView

from uniworld.models import Course


def heartbeat(request):
    return HttpResponse("alive")


def home(request):
    return render(request, 'home.html')


class CourseListView(ListView):
    model = Course
    context_object_name = 'course_list'

