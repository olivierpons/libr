from django import forms


class AddressForm(forms.Form):
    street = forms.CharField(max_length=200)
    street_details = forms.CharField(max_length=200, required=None)
    zip_code = forms.CharField(max_length=10)
    city = forms.CharField(max_length=200)
    country = forms.CharField(max_length=200)
    address_type = forms.CharField(max_length=200)
