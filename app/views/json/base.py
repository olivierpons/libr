from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from app.views.mixins import PersonTypedMixin


class BaseJsonView(PersonTypedMixin, generic.View):
    http_method_names = ['get']

    @method_decorator(never_cache)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def json_error(s: str):
        return JsonResponse({'success': False, 'error': s}, safe=False)
