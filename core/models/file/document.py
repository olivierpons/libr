from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from core.models.file.base import BaseFile


class DocumentFile(BaseFile):
    upload_directory = settings.UPLOAD_FOLDER_DOCUMENTS

    actual_file = models.FileField(default=None, null=True, blank=True,
                                   upload_to=BaseFile.generate_filename, )

    @cached_property
    def file_field(self):
        return self.actual_file
