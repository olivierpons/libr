from django.db import models

from core.models.activity_type import ActivityType
from core.models.base import BaseModel
from django.utils.translation import gettext_lazy as _


class Activity(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True,
                            unique=True)
    description = models.TextField(blank=True, null=True)
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE,
                                      blank=True, null=True)

    def __str__(self):
        return f'{self.str_clean(self.name)} ({str(self.activity_type)})'

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
