from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from rules.contrib.views import AutoPermissionRequiredMixin
from django.views import View
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Course

from uniworld.models import Course
from chat.models import Room


def heartbeat(request):
    return HttpResponse("alive")


def home(request):
    return render(request, 'home.html')


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'uniworld/course_list.html'
    context_object_name = 'course_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_add_course'] = self.request.user.has_perm('uniworld.add_course')
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
        return redirect(reverse('course-detail', kwargs={'pk': self.object.pk}))


class CourseCreateView(AutoPermissionRequiredMixin, CreateView):
    model = Course
    fields = ['name', 'description']
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        response = super(CourseCreateView, self).form_valid(form)
        
        # Create associated chat room
        room = Room.objects.create(name=f"Chat for {form.instance.name}")
        form.instance.chat_room = room
        form.instance.save()
        
        messages.success(self.request, "The course was created successfully.")
        return response


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
        return redirect('course-detail', pk=pk)


def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrolled_students_list = course.students.all().order_by('last_name', 'first_name')
    
    paginator = Paginator(enrolled_students_list, 10)  # Show 10 students per page
    page_number = request.GET.get('page')
    enrolled_students = paginator.get_page(page_number)

    context = {
        'course': course,
        'enrolled_students': enrolled_students,
        'is_enrolled': request.user in course.students.all(),
    }
    return render(request, 'uniworld/course_detail.html', context)


@login_required
def remove_student(request, course_id, student_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user != course.teacher:
        return HttpResponseForbidden("You don't have permission to remove students from this course.")
    
    if request.method == 'POST':
        student = get_object_or_404(course.students, pk=student_id)
        course.students.remove(student)
        messages.success(request, f"{student.first_name} {student.last_name} has been removed from the course.")
    
    return redirect('course-detail', pk=course_id)