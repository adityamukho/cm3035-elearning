from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
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
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.models import Group
import re

def heartbeat(request):
    return HttpResponse("alive")


def home(request):
    return render(request, 'home.html')


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'uniworld/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.exclude(blocked_students=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_add_course'] = self.request.user.has_perm('uniworld.add_course')
        return context


class CourseDetailView(AutoPermissionRequiredMixin, DetailView):
    model = Course
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrolled_students_list = self.object.students.all()
        
        if self.request.user == self.object.teacher:
            search_query = self.request.GET.get('search')
            if search_query:
                enrolled_students_list = enrolled_students_list.filter(
                    Q(first_name__icontains=search_query) | 
                    Q(last_name__icontains=search_query) |
                    Q(email__icontains=search_query)
                )
        
        enrolled_students_list = enrolled_students_list.order_by('last_name', 'first_name')
        
        paginator = Paginator(enrolled_students_list, 10)  # Show 10 students per page
        page_number = self.request.GET.get('page')
        enrolled_students = paginator.get_page(page_number)

        blocked_students_list = self.object.blocked_students.all().order_by('last_name', 'first_name')
        blocked_paginator = Paginator(blocked_students_list, 10)  # Show 10 blocked students per page
        blocked_page_number = self.request.GET.get('blocked_page')
        blocked_students = blocked_paginator.get_page(blocked_page_number)

        context['enrolled_students'] = enrolled_students
        context['blocked_students'] = blocked_students
        context['is_enrolled'] = self.request.user in self.object.students.all()
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


class RemoveStudentView(LoginRequiredMixin, View):
    def post(self, request, course_id, student_id):
        course = get_object_or_404(Course, pk=course_id)
        if request.user != course.teacher:
            return HttpResponseForbidden("You don't have permission to remove students from this course.")
        
        student = get_object_or_404(course.students, pk=student_id)
        course.students.remove(student)
        messages.success(request, f"{student.first_name} {student.last_name} has been removed from the course.")
        
        return redirect('course-detail', pk=course_id)


class BlockStudentView(LoginRequiredMixin, View):
    def post(self, request, course_id, student_id):
        course = get_object_or_404(Course, pk=course_id)
        if request.user != course.teacher:
            return HttpResponseForbidden("You don't have permission to block students from this course.")
        
        student = get_object_or_404(get_user_model(), pk=student_id)
        course.students.remove(student)
        course.blocked_students.add(student)
        messages.success(request, f"{student.first_name} {student.last_name} has been blocked from the course.")
        
        return redirect('course-detail', pk=course_id)


class AddStudentsView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        if request.user != course.teacher:
            return HttpResponseForbidden("You don't have permission to add students to this course.")
        
        student_emails = request.POST.get('student_emails', '').split(',')
        student_emails = [re.search(r'[\w\.-]+@[\w\.-]+', email).group() for email in student_emails]
        
        added_count = 0
        for email in student_emails:
            try:
                student = get_user_model().objects.get(email=email)
                if student not in course.students.all() and student not in course.blocked_students.all():
                    course.students.add(student)
                    added_count += 1
            except get_user_model().DoesNotExist:
                pass
        
        messages.success(request, f"{added_count} student(s) have been added to the course.")
        return redirect('course-detail', pk=course_id)


class StudentSearchView(View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        course_id = request.GET.get('course_id')
        
        User = get_user_model()
        students_group = Group.objects.get(name='students')
        students = User.objects.filter(
            Q(first_name__icontains=term) | 
            Q(last_name__icontains=term) | 
            Q(email__icontains=term),
            groups=students_group
        ).exclude(
            enrolled_courses__id=course_id
        )[:10]
        
        results = [{'label': f"{s.first_name} {s.last_name} ({s.email})", 'value': s.email} for s in students]
        return JsonResponse(results, safe=False)


class CourseEnrollView(View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        if user in course.blocked_students.all():
            messages.error(request, "You are blocked from enrolling in this course.")
            return redirect('course-detail', pk=course_id)

        if user not in course.students.all():
            course.students.add(user)
            messages.success(request, "You have successfully enrolled in the course.")
        else:
            messages.info(request, "You are already enrolled in this course.")

        return redirect('course-detail', pk=course_id)


class UnblockStudentView(LoginRequiredMixin, View):
    def post(self, request, course_id, student_id):
        course = get_object_or_404(Course, pk=course_id)
        if request.user != course.teacher:
            return HttpResponseForbidden("You don't have permission to unblock students from this course.")
        
        student = get_object_or_404(get_user_model(), pk=student_id)
        course.blocked_students.remove(student)
        messages.success(request, f"{student.first_name} {student.last_name} has been unblocked from the course.")
        
        return redirect('course-detail', pk=course_id)

class SearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        results = []

        if query:
            # Search courses
            courses = Course.objects.filter(name__icontains=query)
            for course in courses:
                results.append({
                    'label': course.name,
                    'url': reverse('course-detail', args=[course.pk])
                })

            # Search users in 'teachers' or 'students' groups
            User = get_user_model()
            users = User.objects.filter(
                Q(groups__name='teachers') | Q(groups__name='students'),
                Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
            )
            for user in users:
                results.append({
                    'label': f"{user.first_name} {user.last_name} ({user.email})",
                    'url': reverse('profile', args=[user.pk])
                })

        return JsonResponse({'results': results})
