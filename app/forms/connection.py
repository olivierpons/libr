from django import forms


class ConnectionForm(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(max_length=200)

    def clean_username(self):
        return self.cleaned_data['username']
