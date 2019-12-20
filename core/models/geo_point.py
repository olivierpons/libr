from django.db import models

from core.models.base import BaseModel
from django.utils.translation import ugettext_lazy as _


class GeoPoint(BaseModel):
    place_id = models.CharField(max_length=100, default='',
                                null=True, blank=True)
    lat = models.DecimalField(default=None, null=True, blank=True,
                              max_digits=19, decimal_places=10)
    lng = models.DecimalField(default=None, null=True, blank=True,
                              max_digits=19, decimal_places=10)

    # formatted_address should be according to the language, like:
    # language = models.ForeignKey(Language, ...)
    # but here it's always 'fr'.
    # Nevertheless google returns  formatted address according to language:
    # 'en': "Beijing, Beijing, China", 'fr': "P\u00e9kin, P\u00e9kin, Chine" ...
    formatted_address = models.CharField(max_length=200, default=u'', null=True,
                                         blank=True)

    def __str__(self):
        return _('(lat: {}, lng: {})').format(self.lat if self.lat else '?',
                                              self.lng if self.lng else '?')
