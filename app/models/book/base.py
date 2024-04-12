from django.db import models

from core.models.entity import Entity


class Book(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Entity, related_name='authored_books')
    publisher = models.ForeignKey(Entity, on_delete=models.CASCADE,
                                  related_name='published_books')
    publication_date = models.DateField(default=None)
