from django.db import models

from core.models.base import BaseModel
from core.models.person import Person


class LinkType(BaseModel):
    link_type = models.CharField(max_length=200, blank=True, null=True)
    creator = models.ForeignKey(Person, on_delete=models.CASCADE,
                                blank=True, null=True)
