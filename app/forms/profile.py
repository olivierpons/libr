from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
import re

from core.models.entity import EntityPhone
from core.models.person import Person


class EntityPhoneForm(forms.ModelForm):
    class Meta:
        model = EntityPhone
        fields = ('type', 'phone')


EntityPhoneFormSet = inlineformset_factory(Person, EntityPhone,
                                           form=EntityPhoneForm, extra=1)


class ProfileForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'] = forms.CharField(
            label=_("First name"), max_length=200, required=False,
            widget=forms.TextInput(
                attrs={'class': 'form-control',
                       'focused': True,
                       'placeholder': _("Ex.: : John")}))
        self.fields['last_name'] = forms.CharField(
            label=_("Last name"), max_length=200, required=False,
            widget=forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': _("Ex.: Doe")}))
        self.fields['email'] = forms.CharField(
            label=_("email"), max_length=200,
            widget=forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': _("Ex.: john.doe@gmail.com")}))
        self.fields['username'] = forms.CharField(
            label=_("User name"), max_length=200,
            widget=forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': _("Ex: john_doe")}))
        self.fields['old_password'] = forms.CharField(
            label=_("Old password"), max_length=200, required=False,
            widget=forms.PasswordInput(
                attrs={'class': 'form-control',
                       'placeholder': _("only if you want to change")}))
        self.fields['password'] = forms.CharField(
            label=_("Password"), max_length=200, required=False,
            widget=forms.PasswordInput(
                attrs={'class': 'form-control',
                       'placeholder': _("only if you want to change")}))
        self.fields['password_repeat'] = forms.CharField(
            label=_("Repeat password"), max_length=200, required=False,
            widget=forms.PasswordInput(
                attrs={'class': 'form-control',
                       'placeholder': _("only if you want to change")}))

    EMAIL_REGEX = re.compile(
        r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*'
        r'|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]'
        r'|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@'
        r'(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9]'
        r'(?:[a-z0-9-]*[a-z0-9])?|'
        r'\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}'
        r'(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|'
        r'[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|'
        r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(self.EMAIL_REGEX, email):
            self.add_error('email', _("Not a valid email"))
        return email
