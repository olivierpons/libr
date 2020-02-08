from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.base import BaseModel


class Address(BaseModel):
    place_id = models.CharField(max_length=100, default='', null=True,
                                blank=True)
    lat = models.DecimalField(default=None, null=True, blank=True,
                              max_digits=19, decimal_places=10)
    lng = models.DecimalField(default=None, null=True, blank=True,
                              max_digits=19, decimal_places=10)
    summary = models.CharField(max_length=250, blank=True, null=True)
    details = models.TextField(default=None, blank=True, null=True)

    postal_code = models.CharField(max_length=25, blank=True, null=True,
                                   default=None)

    def details_cleaned(self):
        # details were made to handle tons of data we got from nominatim
        # or google: we registered the results AFTER a '-- COMPUTED --' string:
        if self.details is None:
            return None
        idx = self.details.find('-- COMPUTED --')
        if idx >= 0:  # ignore what's after
            result = self.details[:idx].strip()
        else:
            result = self.details.strip()
        return result if result else None

    def as_dict(self):
        return {'summary': self.summary or None,
                'lat': self.lat or None,
                'lng': self.lng or None,
                'details': self.details_cleaned() or None,
                'postal_code': self.postal_code or None}

    def __str__(self):
        # if self.lat is not None and self.lng is not None:
        #     coords = f'({self.str_clean(self.lat)}/' \
        #              f'{self.str_clean(self.lng)}) '
        # else:
        #     coords = '(?,?)'
        return f'{self.str_clean(self.place_id)} ' \
               f'{_("(found)") if self.way else _("(empty)")} / ' \
               f'{self.str_clean(self.summary, max_len=70)} / ' \
               f'{self.str_clean(self.details, max_len=30)} / ' \
               f'{self.str_clean(self.way, max_len=30)}'.strip()

    def save(self, *args, **kwargs):
        if self.way and self.lat is None and self.lat is None:
            center_point = self.way.centroid
            self.lng, self.lat = center_point.coords

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
