from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.forms import widgets
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=200,
        widget=widgets.EmailInput(attrs={'class': 'form-control',
                                         'placeholder': _("Email")}))
    password = forms.CharField(max_length=200, widget=widgets.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        self.email_or_password_error = _("email (or password) invalid")
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            self.add_error('email', _("You must provide an email"))
            return None
        try:
            self.user_cache = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            self.add_error('email', self.email_or_password_error)
            self.add_error('password', self.email_or_password_error)
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            self.add_error('email', _("You must provide a password"))
            return None
        return password

    def clean(self):
        if len(self.errors):
            return self.cleaned_data

        password = self.cleaned_data.get('password')
        if password:
            self.user_cache = authenticate(self.request,
                                           username=self.user_cache.username,
                                           password=password)
            if self.user_cache is None:
                self.add_error(None, self.email_or_password_error)
            elif not self.user_cache.is_active:
                self.add_error('email', _("User is not active yet"))

        return self.cleaned_data

    def get_user(self):
        return self.user_cache
