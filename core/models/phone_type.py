from django.db import models

from core.models.base import BaseModel
from django.utils.translation import gettext_lazy as _


class PhoneType(BaseModel):
    PHONE_TYPE_MOBILE = 'mobile'
    PHONE_TYPE_EMERGENCY = 'emergency'
    PHONE_TYPE_HOME = 'home'
    PHONE_TYPE_WORK = 'work'

    PHONE_TYPES = [
        (PHONE_TYPE_MOBILE, _("Mobile")),
        (PHONE_TYPE_EMERGENCY, _("Emergency")),
        (PHONE_TYPE_HOME, _("Home")),
        (PHONE_TYPE_WORK, _("Work")),
    ]

    type = models.CharField(
        max_length=50,
        choices=PHONE_TYPES,
        default=PHONE_TYPE_MOBILE,
    )

    def __str__(self):
        return f'{self.get_type_display()}'
