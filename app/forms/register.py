from collections import OrderedDict

from django import forms
from django.forms import widgets
from django.utils.translation import gettext_lazy as _


class RegisterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def _attrs(place_holder, fa):
            return {'placeholder': place_holder,
                    'class': 'hqf-fa form-control',
                    'fa': fa}

        first_name = forms.CharField(
            max_length=200,
            widget=widgets.TextInput(
                attrs=_attrs(_("First name - (ex. John)"), 'fas fa-user')))

        last_name = forms.CharField(
            max_length=200,
            widget=widgets.TextInput(
                attrs=_attrs(_("Last name - (ex. Doe)"), 'fas fa-user')))
        email = forms.CharField(
            max_length=200,
            widget=widgets.EmailInput(
                attrs=_attrs(_("john.doe@gmail.com"), 'fas fa-envelope')))
        password_1 = forms.CharField(
            max_length=200,
            widget=widgets.PasswordInput(
                attrs=_attrs(_("Password"), 'fas fa-lock')))
        password_2 = forms.CharField(
            max_length=200,
            widget=widgets.PasswordInput(
                attrs=_attrs(_("Retype password"), 'fas fa-lock')))

        self.fields = OrderedDict([
            ('first_name', first_name),
            ('last_name', last_name),
            ('email', email),
            ('password_1', password_1),
            ('password_2', password_2),
        ])

    def clean(self):
        password_1 = self.cleaned_data['password_1']
        password_2 = self.cleaned_data['password_2']
        if password_1 != password_2:
            self.add_error('password_1', _("Passwords are different!"))
            self.add_error('password_2', _("Passwords are different!"))
        return super().clean()
