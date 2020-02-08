from django.db import models

from core.models.file.image import ImageFile


class BookPage(models.Model):
    images = models.ForeignKey(ImageFile, on_delete=models.CASCADE,
                               related_name='book_pages')
