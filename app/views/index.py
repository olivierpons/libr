from django.views import generic

from app.views.mixins import PersonTypedMixin


class HomeView(PersonTypedMixin, generic.TemplateView):
    # template_name = 'index.html'
    template_name = 'material-design-pro/home.html'
