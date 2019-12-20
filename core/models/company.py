from django.contrib.auth.models import User
from django.db import models

from core.models.entity import Entity


class CompanyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_physical=True)


class Company(Entity):
    objects = CompanyManager()
    user = models.OneToOneField(User, blank=True, null=True,
                                on_delete=models.CASCADE)
