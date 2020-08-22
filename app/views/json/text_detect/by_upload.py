import binascii
import math
import os
import tempfile
from base64 import b64decode

import cv2
import pytesseract
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from app.views.json.base import BaseJsonView


class TextDetectByUploadView(BaseJsonView):
    http_method_names = ['post']
    EXTENSION_MAPPING = {'jpg': 'jpg',
                         'jpeg': 'jpg',
                         'png': 'png'}

    def post(self, request, *args, **kwargs):
        img_base64 = request.POST.get('img')
        if not img_base64:
            return self.json_error(_("image required"))
        # get file type: img_base64 begins by 'data:image/jpeg;base64,'
        img_type = img_base64.split('data:image/', 1)
        if not len(img_type):
            return self.json_error(_("bad file type"))
        img_type = img_type[1].split(';', 1)
        if not len(img_type):
            return self.json_error(_("bad type of image"))
        try:
            img_type = self.EXTENSION_MAPPING[img_type[0].lower()]
        except KeyError:
            return self.json_error(_("bad type of image"))

        # use only the part without 'data:image/jpeg;base64,':
        img_base64 = img_base64.split('base64,', 1)
        if not len(img_base64):
            return self.json_error(_("bad image data"))
        try:
            image_data = b64decode(img_base64[1])
        except binascii.Error:
            return self.json_error(_("bad image data"))

        f, tmp_name = tempfile.mkstemp(suffix=f'.{img_type}')
        try:
            os.write(f, image_data)
            os.close(f)
            img = cv2.imread(tmp_name)
        finally:
            os.remove(tmp_name)

        (height, width) = img.shape[:2]
        # round to upper int multiple of 32:
        height = max(32, math.ceil(height / 32) * 32)
        width = max(32, math.ceil(width / 32) * 32)
        img = cv2.resize(img, (width, height))
        return JsonResponse({'success': True,
                             'result': pytesseract.image_to_string(img)},
                            safe=False)
