from django import forms
from django.forms import formset_factory, widgets

from core.models.address_type import AddressType


class AddressForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        address_types = [(p.pk, p.name) for p in AddressType.objects.all()]
        self.fields['type'] = forms.ChoiceField(
            choices=address_types,
            widget=forms.Select(attrs={'class': 'form-control col-sm-3'}))

        self.fields['details'] = forms.CharField(
            max_length=200,
            widget=widgets.TextInput(
                attrs={'class': 'form-control osm-widget'}))


AddressFormset = formset_factory(AddressForm, extra=1)
