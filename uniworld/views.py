from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from rules.contrib.views import AutoPermissionRequiredMixin
from django.views import View

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrolled_students'] = self.object.students.all()
        context['is_enrolled'] = self.request.user in context['enrolled_students']
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_authenticated and request.user != self.object.teacher:
            if request.user not in self.object.students.all():
                self.object.students.add(request.user)
                messages.success(request, f"You have successfully enrolled in {self.object.name}.")
            else:
                messages.info(request, f"You are already enrolled in {self.object.name}.")
        return redirect(reverse('course', kwargs={'pk': self.object.pk}))


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


class CourseLeaveView(View):
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        if request.user.is_authenticated and request.user in course.students.all():
            course.students.remove(request.user)
            messages.success(request, f"You have successfully left the course '{course.name}'.")
        return redirect('course', pk=pk)