from django.db import models

from core.models.base import BaseModel
from django.utils.translation import gettext_lazy as _


class Activity(BaseModel):
    class Type(models.IntegerChoices):
        UNKNOWN = 1, _("Unknown")
        PROFESSION = 2, _("Profession")

    type = models.IntegerField(default=Type.UNKNOWN, choices=Type.choices)

    name = models.CharField(max_length=200, blank=True, null=True,
                            unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.str_clean(self.name)} ({str(self.get_type_display())})'

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
