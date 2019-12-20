from django.db import models

from core.models.base import BaseModel


class ActivityType(BaseModel):
    DEFAULT_TYPE = 1
    PROFESSION_TYPE = 2

    ACTIVITY_TYPE_CHOICES = [
        (DEFAULT_TYPE, 'Default'),
        (PROFESSION_TYPE, 'Profession'),
    ]

    name = models.IntegerField(choices=ACTIVITY_TYPE_CHOICES,
                               blank=True, null=True)

    def __str__(self):
        return f'{self.str_clean(self.name)}'
