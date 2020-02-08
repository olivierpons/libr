from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils.timezone import now
from django.utils import timezone, formats
from django.utils.formats import date_format
from django.utils.dateformat import DateFormat
from django.utils.dateformat import format as datetime_format


class BaseModel(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('Created'))
    date_last_modif = models.DateTimeField(auto_now=True,
                                           verbose_name=_('Last changed'))
    date_v_start = models.DateTimeField(
        default=timezone.now,
        editable=True,
        verbose_name=_("V. start")
    )
    date_v_end = models.DateTimeField(
        default=None,
        null=True,
        editable=True,
        verbose_name=_("V. end"),
        blank=True
    )

    @staticmethod
    def date_relative(d, most_recent=None):
        if d is None:
            return _("No date")
        if most_recent is None:
            diff = now() - d
        else:
            diff = most_recent - d
        s = diff.seconds
        if diff.days > 7 or diff.days < 0:
            if d.year == now().year:
                return date_format(d, 'MONTH_DAY_FORMAT', use_l10n=True)
            return date_format(d, 'SHORT_DATE_FORMAT', use_l10n=True)
        elif diff.days == 1:
            return _("1 day ago")
        elif diff.days > 1:
            return _("{} days ago").format(diff.days)
        elif s <= 1:
            return _("Just now")
        elif s < 60:
            return _("{} seconds ago").format(s)
        elif s < 120:
            return _("1 minute ago")
        elif s < 3600:
            return _("{} minutes ago").format(s // 60)
        elif s < 7200:
            return _("1 hour ago")
        else:
            return _("{} hours ago").format(s // 3600)

    def date_creation_relative(self):
        return self.date_relative(self.date_creation)

    @staticmethod
    def date_input(dt):
        if dt is None:
            return None
        a = formats.get_format('DATE_INPUT_FORMATS')[1]
        # transform '%d/%m/%y' into 'd/m/Y'
        for old, new in [('%', ''), ('y', 'Y'), ]:
            a = a.replace(old, new)
        return DateFormat(dt).format(a)

    @staticmethod
    def desc_date(dt, if_none=_("(no date)")):
        retour = BaseModel.date_input(dt)
        return if_none if retour is None else retour

    @staticmethod
    def datetime_input(dt):
        if dt is None:
            return None
        a = formats.get_format('DATETIME_INPUT_FORMATS')[0]
        # transform '%d/%m/%y' into 'd/m/Y'
        for old, new in [('%', ''), ('y', 'Y'), ]:
            a = a.replace(old, new)
        return DateFormat(dt).format(a)

    @staticmethod
    def desc_datetime(dt, if_none=_("(no date)")):
        retour = BaseModel.datetime_input(dt)
        return if_none if retour is None else retour

    @staticmethod
    def date_time_to_int(value):
        return int(datetime_format(value, 'U')) if value is not None else None

    @staticmethod
    def str_clean(a, if_none='', sep='', max_len=30):
        if a is None:
            return if_none
        b = str(a)  # ! force to str()
        if len(b) > max_len:
            return '{}{}...'.format(sep, b[:max_len])
        return '{}{}'.format(sep, b)

    class Meta:
        abstract = True
        ordering = ['date_v_start']
