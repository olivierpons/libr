from django.contrib.auth.views import LoginView

from app.forms.login import LoginForm


class LibrLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'
