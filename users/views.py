from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView

from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm


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
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=user.profile)

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'is_own_profile': user == request.user
        }

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
