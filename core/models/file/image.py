import os
from os.path import dirname, basename
from pathlib import Path

import PIL
from PIL import Image, ExifTags
from django.db import models
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.functional import cached_property

from libr import settings
from libr.settings import THUMBNAIL_SUBDIRECTORY, MEDIA_ROOT, \
    UPLOAD_FOLDER_IMAGES
from .base import BaseFile


class ImageFile(BaseFile):
    upload_directory = settings.UPLOAD_FOLDER_IMAGES

    image_file = models.ImageField(default=None, null=True, blank=True,
                                   upload_to=BaseFile.generate_filename, )

    @cached_property
    def file_field(self):
        return self.image_file

    # region - url_thumbnail() -
    def url_thumbnail(self, default=None):
        if self.file_field:
            relative_name = self.full_upload_path.joinpath(
                THUMBNAIL_SUBDIRECTORY, self.full_filename.name
            ).relative_to(Path(settings.MEDIA_ROOT).resolve())
            return reverse_lazy('url_public', args=(relative_name,))
        if default:
            return static(default)
        return static('img/no-image-yet.jpg')
    # endregion - url_thumbnail() -

    # region - generate_thumbnail() -
    def generate_thumbnail(self, img, dimensions=settings.THUMBNAIL_DIMENSIONS):
        w_thumbnail, h_thumbnail = dimensions
        # calculate how much we need to resize for both dimensions:
        percent = min(w_thumbnail / float(img.size[0]),
                      h_thumbnail / float(img.size[1]))
        img = img.resize((int(float(img.size[0]) * percent),
                          int(float(img.size[1]) * percent)),
                         PIL.Image.ANTIALIAS)

        full_filename = Path(self.full_filename)
        path_thumbnail = full_filename.parent.joinpath(THUMBNAIL_SUBDIRECTORY)
        try:
            os.makedirs(path_thumbnail)
        except FileExistsError:
            pass
        img.save(path_thumbnail.joinpath(full_filename.name))
    # endregion - generate_thumbnail() -

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # after update, if image is rotated, make it "the right way":
        img = Image.open(self.full_filename)
        try:
            # rotation img code
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    try:
                        exif = dict(img._getexif().items())
                        if exif[orientation] == 6:
                            img = img.rotate(-90, expand=True)
                        elif exif[orientation] == 8:
                            img = img.rotate(90, expand=True)
                        elif exif[orientation] == 3:
                            img = img.rotate(180, expand=True)
                        elif exif[orientation] == 2:
                            img = img.transpose(
                                Image.FLIP_LEFT_RIGHT, expand=True)
                        elif exif[orientation] == 5:
                            img = img.rotate(-90).transpose(
                                Image.FLIP_LEFT_RIGHT, expand=True)
                        elif exif[orientation] == 7:
                            img = img.rotate(90, expand=True).transpose(
                                Image.FLIP_LEFT_RIGHT, expand=True)
                        elif exif[orientation] == 4:
                            img = img.rotate(180).transpose(
                                Image.FLIP_LEFT_RIGHT, expand=True)
                        break
                    except ZeroDivisionError:
                        # error unknown due to PIL/TiffImagePlugin.py buggy
                        # -> ignore this "rotation img" code, just continue
                        break
        except (AttributeError, KeyError, IndexError):
            # cases: image don't have getexif
            # -> ignore this "rotation img" code, just continue
            pass
        self.generate_thumbnail(img)
