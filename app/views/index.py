from django.views import generic

from app.views.mixins import PersonTypedMixin


class IndexView(PersonTypedMixin, generic.TemplateView):
    template_name = 'index.html'
