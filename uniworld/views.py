from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rules.contrib.views import AutoPermissionRequiredMixin
from rules.contrib.rest_framework import AutoPermissionViewSetMixin
from rest_framework.exceptions import PermissionDenied

from chat.models import Room
from uniworld.forms import CourseMaterialForm, LectureForm, AssignmentForm, AssignmentQuestionForm, MCQOptionFormSet
from uniworld.models import (
    Course, CourseMaterial, Lecture, Assignment, AssignmentSubmission,
    AssignmentQuestion, QuestionResponse, MCQOption, Feedback
)
from uniworld.serializers import (
    CourseSerializer, CourseMaterialSerializer, LectureSerializer,
    AssignmentSerializer, AssignmentQuestionSerializer,
    AssignmentSubmissionSerializer, QuestionResponseSerializer,
    MCQOptionSerializer, FeedbackSerializer
)

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
        queryset = Course.objects.exclude(blocked_students=self.request.user)
        filter_param = self.request.GET.get('filter')

        if filter_param == 'my_courses':
            if self.request.user.groups.filter(name='teachers').exists():
                queryset = queryset.filter(teacher=self.request.user)
            else:
                queryset = queryset.filter(students=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_add_course'] = self.request.user.has_perm('uniworld.add_course')
        return context


class CourseDetailView(AutoPermissionRequiredMixin, DetailView):
    model = Course
    context_object_name = 'course'
    template_name = 'uniworld/course_detail.html'

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
        context['feedback_list'] = self.object.feedback.all().order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_authenticated and request.user != self.object.teacher:
            if request.user not in self.object.students.all():
                self.object.students.add(request.user)
                messages.success(request, f"You have successfully enrolled in {self.object.name}.")
            else:
                messages.info(request, f"You are already enrolled in {self.object.name}.")
        return redirect(reverse('course-view', kwargs={'pk': self.object.pk}))


class CourseCreateView(AutoPermissionRequiredMixin, CreateView):
    model = Course
    fields = ['name', 'description']
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        response = super(CourseCreateView, self).form_valid(form)
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


class CourseLeaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        if not request.user.has_perm(Course.get_perm('leave_course'), course):
            return HttpResponseForbidden("You don't have permission to leave this course.")

        course.students.remove(request.user)
        messages.success(request, f"You have successfully left the course '{course.name}'.")
        return redirect('course-view', pk=pk)


class RemoveStudentView(LoginRequiredMixin, View):
    def post(self, request, course_id, student_id):
        course = get_object_or_404(Course, pk=course_id)
        if not request.user.has_perm(Course.get_perm('remove_student'), course):
            return HttpResponseForbidden("You don't have permission to remove students from this course.")

        student = get_object_or_404(course.students, pk=student_id)
        course.students.remove(student)
        messages.success(request, f"{student.first_name} {student.last_name} has been removed from the course.")
        
        return redirect('course-view', pk=course_id)


class BlockStudentView(LoginRequiredMixin, View):
    def post(self, request, course_id, student_id):
        course = get_object_or_404(Course, pk=course_id)
        if not request.user.has_perm(Course.get_perm('block_student'), course):
            return HttpResponseForbidden("You don't have permission to block students from this course.")
        
        try:
            student = get_user_model().objects.get(pk=student_id)
            
            # If the student is enrolled, unenroll them first
            if student in course.students.all():
                course.students.remove(student)
                messages.info(request, f"{student.first_name} {student.last_name} has been unenrolled from the course.")
            
            # Block the student
            if student not in course.blocked_students.all():
                course.blocked_students.add(student)
                messages.success(request, f"{student.first_name} {student.last_name} has been blocked from the course.")
            else:
                messages.info(request, f"{student.first_name} {student.last_name} is already blocked from this course.")
        
        except get_user_model().DoesNotExist:
            messages.error(request, f"No user found with ID {student_id}.")
        
        return redirect('course-view', pk=course_id)


class AddStudentsView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        if not request.user.has_perm(Course.get_perm('enroll_student'), course):
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
        return redirect('course-view', pk=course_id)


class StudentSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        course_id = request.GET.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        if not request.user.has_perm(Course.get_perm('enroll_student'), course):
            return HttpResponseForbidden("You don't have permission to enroll students in this course.")
        
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


class CourseEnrollView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if not request.user.has_perm(Course.get_perm('enroll_self'), course):
            return HttpResponseForbidden("You don't have permission to enroll in this course.")

        user = request.user

        if user in course.blocked_students.all():
            messages.error(request, "You are blocked from enrolling in this course.")
            return redirect('course-view', pk=course_id)

        if user not in course.students.all():
            course.students.add(user)
            messages.success(request, "You have successfully enrolled in the course.")
        else:
            messages.info(request, "You are already enrolled in this course.")

        return redirect('course-view', pk=course_id)


class UnblockStudentView(LoginRequiredMixin, View):
    def post(self, request, course_id, student_id):
        course = get_object_or_404(Course, pk=course_id)
        if not request.user.has_perm(Course.get_perm('unblock_student'), course):
            return HttpResponseForbidden("You don't have permission to unblock students from this course.")

        student = get_object_or_404(get_user_model(), pk=student_id)
        course.blocked_students.remove(student)
        messages.success(request, f"{student.first_name} {student.last_name} has been unblocked from the course.")
        
        return redirect('course-view', pk=course_id)

class SearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        results = []

        if query:
            # Search courses
            courses = Course.objects.filter(name__icontains=query)
            for course in courses:
                results.append({
                    'label': course.name,
                    'url': reverse('course-view', args=[course.pk])
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

class CourseFeedbackView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        if not request.user.has_perm(Course.get_perm('add_feedback'), course):
            return HttpResponseForbidden("You don't have permission to add feedback for this course.")
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        if rating:
            Feedback.objects.create(
                course=course,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Your feedback has been submitted.")
        else:
            messages.error(request, "Please provide a rating.")

        return redirect('course-view', pk=course_id)
    
class CourseMaterialListView(LoginRequiredMixin, ListView):
    model = CourseMaterial
    template_name = 'uniworld/course_material.html'
    context_object_name = 'course_material'

    def get_queryset(self):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        if not self.request.user.has_perm(Course.get_perm('view'), course):
            return HttpResponseForbidden("You don't have permission to view this course material.")
        return course.materials.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return context

class AddCourseMaterialView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        if not request.user.has_perm(Course.get_perm('add_course_material'), course):
            return HttpResponseForbidden("You don't have permission to add course material to this course.")
        
        material_form = CourseMaterialForm()
        lecture_form = LectureForm()
        assignment_form = AssignmentForm()
        return render(request, 'uniworld/add_course_material.html', {
            'course': course,
            'material_form': material_form,
            'lecture_form': lecture_form,
            'assignment_form': assignment_form,
        })

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        if request.user != course.teacher:
            return redirect('course-view', pk=course_id)
        
        material_form = CourseMaterialForm(request.POST)
        if material_form.is_valid():
            material = material_form.save(commit=False)
            material.course = course
            material.save()
            
            if material.type == 'lecture':
                lecture_form = LectureForm(request.POST, request.FILES)
                if lecture_form.is_valid():
                    lecture = lecture_form.save(commit=False)
                    lecture.material = material
                    lecture.save()
            elif material.type == 'assignment':
                assignment_form = AssignmentForm(request.POST)
                if assignment_form.is_valid():
                    assignment = assignment_form.save(commit=False)
                    assignment.material = material
                    assignment.save()
            
            return redirect('course-material', course_id=course_id)
        
        lecture_form = LectureForm()
        assignment_form = AssignmentForm()
        return render(request, 'uniworld/add_course_material.html', {
            'course': course,
            'material_form': material_form,
            'lecture_form': lecture_form,
            'assignment_form': assignment_form,
        })
    
class CourseMaterialDetailView(AutoPermissionRequiredMixin, DetailView):
    model = CourseMaterial
    template_name = 'uniworld/course_material_detail.html'
    context_object_name = 'material'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.get_object()
        if material.type == 'lecture':
            lecture = get_object_or_404(Lecture, material=material)
            context['lecture'] = lecture
            context['is_image'] = lecture.document_mime_type and lecture.document_mime_type.startswith("image/")
            context['is_pdf'] = lecture.document_mime_type and lecture.document_mime_type.startswith("application/pdf")
        elif material.type == 'assignment':
            context['assignment'] = get_object_or_404(Assignment, material=material)
        return context
    
class SubmitAssignmentView(LoginRequiredMixin, View):
    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        course = assignment.material.course
        if not request.user.has_perm(Course.get_perm('add_submission'), course):
            return HttpResponseForbidden("You don't have permission to submit assignments for this course.")
        
        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=request.user
        )

        for question in assignment.questions.all():
            answer = request.POST.get(f'question_{question.id}')
            if question.question_type == 'MCQ':
                selected_option = get_object_or_404(MCQOption, pk=answer)
                QuestionResponse.objects.create(
                    submission=submission,
                    question=question,
                    selected_option=selected_option
                )
            elif question.question_type == 'ESSAY':
                QuestionResponse.objects.create(
                    submission=submission,
                    question=question,
                    response_text=answer
                )

        return redirect('course-material', course_id=assignment.material.course.id)

class EditCourseMaterialView(AutoPermissionRequiredMixin, UpdateView):
    model = CourseMaterial
    template_name = 'uniworld/edit_course_material.html'
    form_class = CourseMaterialForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['type'].widget.attrs['readonly'] = True
        form.fields['type'].widget.attrs['disabled'] = True
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.get_object()
        if material.type == 'lecture':
            context['lecture_form'] = LectureForm(instance=material.lecture)
        elif material.type == 'assignment':
            assignment = get_object_or_404(Assignment, material=material)
            context['assignment_form'] = AssignmentForm(instance=assignment)
            context['questions'] = assignment.questions.all()
            context['assignment_id'] = assignment.pk
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        material = self.get_object()
        form.instance.type = material.type  # Ensure the type doesn't change
        material = form.save(commit=False)
        if material.type == 'lecture':
            lecture_form = LectureForm(self.request.POST, self.request.FILES, instance=material.lecture)
            if lecture_form.is_valid():
                lecture_form.save()
        elif material.type == 'assignment':
            assignment = get_object_or_404(Assignment, material=material)
            assignment_form = AssignmentForm(self.request.POST, instance=assignment)
            if assignment_form.is_valid():
                assignment = assignment_form.save(commit=False)
                # Ensure the due_date is timezone aware
                if assignment.due_date and not timezone.is_aware(assignment.due_date):
                    assignment.due_date = timezone.make_aware(assignment.due_date)
                assignment.save()
        material.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('course-material', kwargs={'course_id': self.object.course.id})

class AddAssignmentQuestionView(LoginRequiredMixin, CreateView):
    model = AssignmentQuestion
    form_class = AssignmentQuestionForm
    template_name = 'uniworld/add_assignment_question.html'

    def form_valid(self, form):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['assignment_id'])
        if not self.request.user.has_perm(Assignment.get_perm('add_question'), assignment):
            return HttpResponseForbidden("You don't have permission to add questions to this assignment.")
        
        form.instance.assignment = assignment
        self.object = form.save()
        if form.instance.question_type == 'MCQ':
            formset = MCQOptionFormSet(self.request.POST, instance=self.object)
            if formset.is_valid():
                formset.save()
        return redirect('edit-course-material', pk=assignment.material.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['mcq_formset'] = MCQOptionFormSet(self.request.POST)
        else:
            context['mcq_formset'] = MCQOptionFormSet()
        return context

class DeleteCourseMaterialView(AutoPermissionRequiredMixin, DeleteView):
    model = CourseMaterial
    template_name = 'uniworld/confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('course-material', kwargs={'course_id': self.object.course.id})

    def test_func(self):
        material = self.get_object()
        return self.request.user == material.course.teacher

class DeleteAssignmentQuestionView(AutoPermissionRequiredMixin, DeleteView):
    model = AssignmentQuestion
    template_name = 'uniworld/confirm_delete.html'

    def get_success_url(self):
        question = self.get_object()
        return reverse_lazy('edit-course-material', kwargs={'pk': question.assignment.material.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        material_id = self.object.assignment.material.id
        course_id = self.object.assignment.material.course.id
        response = super().delete(request, *args, **kwargs)
        return response

class CourseSubmissionsView(LoginRequiredMixin, ListView):
    model = AssignmentSubmission
    template_name = 'uniworld/course_submissions.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        if not self.request.user.has_perm(Course.get_perm('add_course_material'), course):
            return HttpResponseForbidden("You don't have permission to view this course submissions.")
        return AssignmentSubmission.objects.filter(assignment__material__course=course).order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(pk=self.kwargs['course_id'])
        return context
    
class ViewSubmissionView(LoginRequiredMixin, View):
    def get(self, request, pk):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        if not request.user.has_perm(AssignmentSubmission.get_perm('view'), submission):
            return HttpResponseForbidden("You don't have permission to view this submission.")

        responses = submission.responses.all()
        is_teacher = request.user == submission.assignment.material.course.teacher
        is_student = request.user == submission.student
        context = {
            'submission': submission,
            'responses': responses,
            'is_teacher': is_teacher,
            'is_student': is_student,
        }
        return render(request, 'uniworld/view_submission.html', context)

class GradeSubmissionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        if not request.user.has_perm(AssignmentSubmission.get_perm('change'), submission):
            return HttpResponseForbidden("You don't have permission to grade this submission.")
        
        feedback = request.POST.get('feedback')

        # Update scores for essay questions
        for response in submission.responses.filter(question__question_type='ESSAY'):
            score = request.POST.get(f'score_{response.id}')
            if score is not None:
                response.score = float(score)
                response.save()

        # Calculate total score
        submission.calculate_total_score()
        submission.feedback = feedback
        submission.save()

        messages.success(request, 'Submission graded successfully. The student will be notified.')
        return redirect('view-submission', pk=submission.pk)

class MySubmissionsView(LoginRequiredMixin, ListView):
    model = AssignmentSubmission
    template_name = 'uniworld/my_submissions.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        if not self.request.user.has_perm(Course.get_perm('add_submission'), course):
            return HttpResponseForbidden("You don't have permission to view this course submissions.")
        return AssignmentSubmission.objects.filter(assignment__material__course=course, student=self.request.user).order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return context

class StudentSubmissionsView(LoginRequiredMixin, ListView):
    model = AssignmentSubmission
    template_name = 'uniworld/student_submissions.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        if not self.request.user.has_perm(Course.get_perm('add_course_material'), course):
            return HttpResponseForbidden("You don't have permission to view this course submissions.")
        student = get_object_or_404(course.students, id=self.kwargs['student_id'])
        return AssignmentSubmission.objects.filter(
            assignment__material__course=course,
            student=student
        ).order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, id=self.kwargs['course_id'])
        context['student'] = get_object_or_404(context['course'].students, id=self.kwargs['student_id'])
        return context
    
class CourseViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseMaterialViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        'create': None,
    }

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        course = get_object_or_404(Course, id=course_id)

        if not request.user.has_perm(Course.get_perm('add_course_material'), course):
            raise PermissionDenied("You do not have permission to add course material to this course.")

        return super().create(request, *args, **kwargs)

class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer

    def create(self, request, *args, **kwargs):
        material_id = request.data.get('material')
        material = get_object_or_404(CourseMaterial, id=material_id)

        if not request.user.has_perm(Course.get_perm('add_course_material'), material.course):
            raise PermissionDenied("You do not have permission to add a lecture to this course.")

        return super().create(request, *args, **kwargs)

class AssignmentViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        'create': None,
    }

    def create(self, request, *args, **kwargs):
        material_id = request.data.get('material')
        material = get_object_or_404(CourseMaterial, id=material_id)

        if not request.user.has_perm(Course.get_perm('add_course_material'), material.course):
            raise PermissionDenied("You do not have permission to add an assignment to this course.")

        return super().create(request, *args, **kwargs)

class AssignmentQuestionViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = AssignmentQuestion.objects.all()
    serializer_class = AssignmentQuestionSerializer
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        'create': None,
    }

    def create(self, request, *args, **kwargs):
        assignment_id = request.data.get('assignment')
        assignment = get_object_or_404(Assignment, material=assignment_id)

        if not request.user.has_perm(Assignment.get_perm('add_question'), assignment):
            raise PermissionDenied("You do not have permission to add a question to this assignment.")

        return super().create(request, *args, **kwargs)

class AssignmentSubmissionViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        'create': None,
    }

    def create(self, request, *args, **kwargs):
        assignment_id = request.data.get('assignment')
        assignment = get_object_or_404(Assignment, material=assignment_id)

        if not request.user.has_perm(Course.get_perm('add_submission'), assignment.material.course):
            raise PermissionDenied("You do not have permission to add a submission to this assignment.")

        return super().create(request, *args, **kwargs)

class QuestionResponseViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = QuestionResponse.objects.all()
    serializer_class = QuestionResponseSerializer
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        'create': None,
    }

    def create(self, request, *args, **kwargs):
        question_id = request.data.get('question')
        question = get_object_or_404(AssignmentQuestion, id=question_id)
        if not request.user.has_perm(AssignmentQuestion.get_perm('add_response'), question):
            raise PermissionDenied("You do not have permission to add a response to this question.")
        return super().create(request, *args, **kwargs)

class MCQOptionViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = MCQOption.objects.all()
    serializer_class = MCQOptionSerializer
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,   
        'create': None,
    }

    def create(self, request, *args, **kwargs):
        question_id = request.data.get('question')
        question = get_object_or_404(AssignmentQuestion, id=question_id)
        if not request.user.has_perm(AssignmentQuestion.get_perm('add_option'), question):
            raise PermissionDenied("You do not have permission to add an option to this question.")
        return super().create(request, *args, **kwargs)

class FeedbackViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        'create': None,
    }

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        course = get_object_or_404(Course, id=course_id)
        if not request.user.has_perm(Course.get_perm('add_feedback'), course):
            raise PermissionDenied("You do not have permission to add feedback to this course.")
        return super().create(request, *args, **kwargs)
