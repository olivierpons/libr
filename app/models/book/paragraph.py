from django.db import models

from app.models.book.page import BookPage


class BookParagraph(models.Model):
    book_page = models.ForeignKey(BookPage, on_delete=models.CASCADE)
