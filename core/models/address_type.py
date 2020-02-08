from django.db import models

from core.models.base import BaseModel


class AddressType(BaseModel):
    name = models.CharField(max_length=200, blank=False, null=False)

    def __str__(self):
        return f'{self.name}'
