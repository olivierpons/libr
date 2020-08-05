import cv2
from imutils.object_detection import non_max_suppression
from django.http import JsonResponse
from django.views import generic

from app.views.mixins import PersonTypedMixin


class TextDetectView(PersonTypedMixin, generic.View):
    http_method_names = ['get']

    @staticmethod
    def get(request, *args, **kwargs):
        return JsonResponse({}, safe=False)