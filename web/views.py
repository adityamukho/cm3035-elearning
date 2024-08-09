from django.shortcuts import render
from django.views.generic.list import ListView

from api.models import Course


def home(request):
    return render(request, 'home.html')


class CourseListView(ListView):
    model = Course
    context_object_name = 'course_list'
    template_name = 'course_list.html'
