import phonenumbers
from django.db import models

from core.models.base import BaseModel
from libr.settings import PHONE_ACCEPTED_FORMAT


class Phone(BaseModel):
    text = models.TextField(blank=False, null=False)

    @staticmethod
    def standardize(phone_number):
        return phonenumbers.format_number(
            phonenumbers.parse(phone_number, PHONE_ACCEPTED_FORMAT),
            phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    def save(self, *args, **kwargs):
        if self.text is not None:
            self.text = self.standardize(self.text)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.text}'
