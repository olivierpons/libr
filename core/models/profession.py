from django.db import models

from core.models.activity import Activity


class ProfessionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Activity.Type.PROFESSION)


class Profession(Activity):
    class Meta:
        proxy = True

    objects = ProfessionManager()

    def __str__(self):
        return f'{self.str_clean(self.name)}'
