from django.contrib.auth.models import Group
from django.db import models

from core.models.base import BaseModel


class Role(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              blank=True, null=True)
