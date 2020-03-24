from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import generic


class LogoutView(LoginRequiredMixin, generic.View):

    @staticmethod
    def get(request):
        logout(request)
        messages.info(request, _("Successful disconnection"))
        return redirect('index')
