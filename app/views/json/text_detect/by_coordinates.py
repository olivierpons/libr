from os import path
from os.path import isfile
from urllib.parse import unquote

import cv2
from imutils.object_detection import non_max_suppression

from django.urls import Resolver404
from django.urls import resolve
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from app.views.json.base import BaseJsonView


class TextDetectByCoordinatesView(BaseJsonView):

    def get(self, request, *args, **kwargs):
        try:
            left = int(request.GET.get('left'))
            top = int(request.GET.get('top'))
            width = int(request.GET.get('width'))
            height = int(request.GET.get('height'))
        except ValueError:
            return self.json_error(_("bad parameters"))
        img_url = request.GET.get('img_url')
        if not img_url:
            return self.json_error(_("bad image"))
        try:
            r = resolve(img_url)
        except Resolver404:
            return self.json_error(_("bad image url"))

        # build full path (using "kwargs", best option? I dont know):
        img_full_path = path.abspath(path.join(r.kwargs['document_root'],
                                               unquote(r.kwargs['path'])))

        if not isfile(img_full_path):
            return self.json_error(_("image not found"))

        left = int(request.GET.get('left'))
        top = int(request.GET.get('top'))
        width = int(request.GET.get('width'))
        height = int(request.GET.get('height'))
        img = cv2.imread(img_full_path)
        crop_img = img[top:top + height, left:left + width]
        cv2.imwrite(f'{img_full_path}.cropped.jpg', crop_img)
        print(f'{img_full_path}.cropped.jpg')
        return JsonResponse({'success': True}, safe=False)
