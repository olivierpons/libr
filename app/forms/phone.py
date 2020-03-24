from django import forms
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _

from phonenumbers import NumberParseException

from core.models.entity import EntityPhone
from core.models.phone import Phone


class PhoneForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'] = forms.ChoiceField(
            choices=EntityPhone.Type,
            widget=forms.Select(attrs={'class': 'form-control col-sm-3'}))
        self.fields['number'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_number(self):
        phone = self.cleaned_data['number']
        if phone:
            try:
                phone = Phone.standardize(phone)
            except NumberParseException:
                self.add_error('number', _("Phone number isn't a known format"))
        return phone


PhoneFormset = formset_factory(PhoneForm, extra=1)
