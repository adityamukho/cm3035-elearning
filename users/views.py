from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView

from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .permissions import IsOwnerOrReadOnly

from django.utils import timezone
from uniworld.models import Assignment
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import UserSerializer, ProfileSerializer
from rules.contrib.rest_framework import AutoPermissionViewSetMixin
from .models import Profile

User = get_user_model()

class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        user = form.save()
        user.groups.add(Group.objects.get(name='students'))
        if user:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        return super(RegisterView, self).form_valid(form)


# noinspection PyMethodMayBeStatic
class ProfileView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        is_own_profile = request.user == user
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=user.profile)

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'is_own_profile': is_own_profile,
        }

        if is_own_profile and user.groups.filter(name='students').exists():
            upcoming_assignments = Assignment.objects.filter(
                Q(material__course__in=user.enrolled_courses.all()) &
                Q(due_date__gt=timezone.now())
            ).order_by('due_date')[:5]  # Get the next 5 upcoming assignments
            context['upcoming_assignments'] = upcoming_assignments

        return render(request, 'users/profile.html', context)

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user != request.user:
            messages.error(request, 'You are not authorized to edit this profile.')

            return redirect('profile', pk=user.pk)

        user_form = UserUpdateForm(
            request.POST,
            instance=user
        )
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, 'Your profile has been updated successfully')

            return redirect('profile', pk=user.pk)
        else:
            context = {
                'user_form': user_form,
                'profile_form': profile_form,
                'is_own_profile': user == request.user
            }
            messages.error(request, 'Error updating you profile')

            return render(request, 'users/profile.html', context)

class UserLoginView(LoginView):
    def get_context_data(self, **kwargs):
        users = User.objects.filter(Q(groups__name='students') | Q(groups__name='teachers')).order_by('id')

        context = super().get_context_data(**kwargs)
        context['users'] = users

        return context

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.instance
        first_name = serializer.validated_data.get('first_name')
        if first_name:
            instance.first_name = first_name
        serializer.save()

class ProfileViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()