from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import RegisterForm


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        user = form.save()
        if user:
            login(self.request, user)

        return super(RegisterView, self).form_valid(form)
