import phonenumbers
from django.db import models

from core.models.base import BaseModel
from libr.settings import PHONE_ACCEPTED_FORMAT


class Phone(BaseModel):
    phone_number = models.TextField(blank=False, null=False)

    @staticmethod
    def standardize(phone_number):
        return phonenumbers.format_number(
            phonenumbers.parse(phone_number, PHONE_ACCEPTED_FORMAT),
            phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    def save(self, *args, **kwargs):
        if self.phone_number is not None:
            self.phone_number = self.standardize(self.phone_number)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.phone_number}'
