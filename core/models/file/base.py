import os
from abc import ABCMeta, abstractmethod
from os.path import splitext, basename

import magic
from django.db import models
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from core.models.base import BaseModel
from core.models.entity import Entity
from core.utils import UidMixin


class BaseFile(UidMixin, BaseModel):
    __metaclass__ = ABCMeta

    upload_directory = ''

    @abstractmethod
    @cached_property
    def file_field(self):
        pass

    def os_full_filename(self, check=True):
        name = os.path.join(settings.MEDIA_ROOT, str(self.file_field))
        return name if not check or os.path.isfile(name) else None

    def url(self, default=None):
        if self.file_field:
            return reverse_lazy('url_public',
                                args=(self.file_field.name[2:]
                                      if self.file_field.name.startswith('./')
                                      else self.file_field.name,))
        if default:
            return staticfiles.static(default)
        return staticfiles.static('img/no-image-yet.jpg')

    @staticmethod
    def relative_url(name, path=None):
        retour = (path if path else '') + name
        # Ex: "profiles/bea536a0/089c/a45b.jpg"
        return retour.replace('-', '/')

    # keep trace of who uploaded the file:
    creator = models.ForeignKey(Entity, on_delete=models.SET_NULL,
                                blank=True, default=None, null=True, )
    description = models.CharField(max_length=200,
                                   blank=True, default=None, null=True, )
    original_filename = models.CharField(max_length=200,
                                         blank=True, default=None, null=True, )

    def __init__(self, *args, **kwargs):
        if self.upload_directory != '':
            if not self.upload_directory.endswith(os.sep):
                self.upload_directory += os.sep
        super().__init__(*args, **kwargs)

    # generate a filename dynamically:
    def generate_filename(self, filename):
        # name like: "bea536a0-089c-a45b.pdf"
        name = self.generate_uid(splitext(basename(filename))[1])
        # final return result like: "profiles/bea536a0/089c/a45b.pdf":
        return self.relative_url(name, self.upload_directory)

    def file_detailed_description(self):
        mime = magic.Magic(mime=True)
        name = self.os_full_filename()
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
        description = self.description or _("No description")
        creator = _("creator: {}").format(str(self.creator or _("no creator")))
        result = f'{self.pk} - {description} ({file_name}) / {creator}'
        if self.date_v_end is None:
            return result
        return _("{} (expired: {})").format(
            result, self.date_relative(self.date_v_end)
        )

    class Meta:
        abstract = True
