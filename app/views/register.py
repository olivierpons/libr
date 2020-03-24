import unidecode
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from app.forms.register import RegisterForm


class RegisterView(generic.FormView):
    template_name = 'register.html'
    form_class = RegisterForm

    def get_success_url(self):
        return reverse('index')

    def form_valid(self, form):
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        password_1 = form.cleaned_data['password_1']
        # hack to make a fake username
        username = email.replace('@', '_at_')
        # remove accents:
        username = unidecode.unidecode(username)
        # replace special chars by '_':
        username.translate({ord(c): '_'
                            for c in r"!@#$%^&*()[]{};:,./<>?\|`~-=+"})

        if User.objects.filter(email=email).exists():
            form.add_error('email', _("Email already used, consider login"))
            return super().form_invalid(form)

        try:
            user = User.objects.create_user(first_name=first_name,
                                            last_name=last_name,
                                            email=email,
                                            username=username,
                                            password=password_1)
        except IntegrityError:
            form.add_error('username', _("Username already taken"))
            return super().form_invalid(form)

        login(self.request, user)

        messages.success(self.request, 'Connecté')
        return super().form_valid(form)
