import os
from abc import ABCMeta, abstractmethod
from os.path import splitext, basename
from pathlib import Path

import magic
from django.db import models
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from core.models.base import BaseModel
from core.models.entity import Entity
from core.utils import UidMixin
from libr import settings


class BaseFile(UidMixin, BaseModel):
    __metaclass__ = ABCMeta

    upload_directory = ''

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # remove last char if it's a separator:
        if cls.upload_directory.endswith(os.sep):
            cls.upload_directory = cls.upload_directory[:-1]

    @abstractmethod
    @cached_property
    def file_field(self):
        pass

    @cached_property
    def full_upload_path(self):
        result = self.full_filename
        return result.resolve().parent if result else None

    @cached_property
    def full_filename(self):
        return Path(settings.MEDIA_ROOT, str(self.file_field)).resolve()

    def url(self, default=None):
        if self.file_field:
            return reverse_lazy('url_public',
                                args=(self.file_field.name[2:]
                                      if self.file_field.name.startswith('./')
                                      else self.file_field.name,))
        if default:
            return static(default)
        return static('img/no-image-yet.jpg')

    # keep trace of who uploaded the file:
    creator = models.ForeignKey(Entity, on_delete=models.SET_NULL,
                                blank=True, default=None, null=True, )
    informations = models.TextField(default=None, null=True, blank=True)
    original_filename = models.CharField(max_length=200,
                                         blank=True, default=None, null=True, )

    def __init__(self, *args, **kwargs):
        if self.upload_directory != '':
            if not self.upload_directory.endswith(os.sep):
                self.upload_directory += os.sep
        super().__init__(*args, **kwargs)

    # generate a filename dynamically:
    def generate_filename(self, filename):
        # name like: "[uid].[ext]" -> example: "bea536a0-089c-a45b.pdf"
        name = self.generate_uid(text_to_append=splitext(basename(filename))[1])
        # final return result like: "profiles/bea536a0/089c/a45b.pdf":
        return os.path.join(self.upload_directory, name.replace('-', '/'))

    def file_detailed_description(self):
        mime = magic.Magic(mime=True)
        name = self.full_filename
        if name is None:
            return None
        result = mime.from_file(name)
        tab = result.split('/')
        if len(tab) == 2:
            if tab[0] == 'image':
                return 'image', tab[1].lower()
            if tab[1] == 'pdf':
                return 'pdf', 'pdf'
        # not handled yet:
        return result.lower(), None

    def file_description(self):
        return self.file_detailed_description()[0]

    def __str__(self):
        file_name = str(self.file_field or _("no file"))
        informations = self.informations or _("No information")
        creator = _("creator: {}").format(str(self.creator or _("no creator")))
        result = f'{self.pk} - {informations} ({file_name}) / {creator}'
        if self.date_v_end is None:
            return result
        return _("{} (expired: {})").format(
            result, self.date_relative(self.date_v_end)
        )

    class Meta:
        abstract = True
