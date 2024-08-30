from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from rules.contrib.views import AutoPermissionRequiredMixin

from uniworld.models import Course


def heartbeat(request):
    return HttpResponse("alive")


def home(request):
    return render(request, 'home.html')


class CourseListView(ListView):
    model = Course

    def get_context_data(self, **kwargs):
        course_list = Course.objects.all()
        enrolled_students = {}

        for course in course_list:
            enrolled_students[course.id] = course.students.count()

        context = super().get_context_data(**kwargs)
        context['course_list'] = course_list
        context['enrolled_students'] = enrolled_students

        return context


class CourseDetailView(DetailView):
    model = Course
    context_object_name = 'course'


class CourseCreateView(AutoPermissionRequiredMixin, CreateView):
    model = Course
    fields = ['name', 'description']
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, "The course was created successfully.")

        return super(CourseCreateView, self).form_valid(form)


class CourseUpdateView(AutoPermissionRequiredMixin, UpdateView):
    model = Course
    fields = ['name', 'description']
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        messages.success(self.request, "The course was updated successfully.")

        return super(CourseUpdateView, self).form_valid(form)


class CourseDeleteView(AutoPermissionRequiredMixin, DeleteView):
    model = Course
    context_object_name = 'course'
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        messages.success(self.request, "The course was deleted successfully.")

        return super(CourseDeleteView, self).form_valid(form)