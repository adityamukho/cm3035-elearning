from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy

from uniworld.models import Course


def heartbeat(request):
    return HttpResponse("alive")


def home(request):
    return render(request, 'home.html')


class CourseListView(ListView):
    model = Course
    context_object_name = 'course_list'


class CourseDetailView(DetailView):
    model = Course
    context_object_name = 'course'


class CourseCreateView(CreateView):
    model = Course
    fields = ['name', 'description']
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "The course was created successfully.")

        return super(CourseCreateView, self).form_valid(form)


class CourseUpdateView(UpdateView):
    model = Course
    fields = ['name', 'description']
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        messages.success(self.request, "The course was updated successfully.")

        return super(CourseUpdateView, self).form_valid(form)


class CourseDeleteView(DeleteView):
    model = Course
    context_object_name = 'course'
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        messages.success(self.request, "The course was deleted successfully.")

        return super(CourseDeleteView, self).form_valid(form)