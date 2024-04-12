from django.core.exceptions import ValidationError
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _


class DaysOfWeek:
    DAYS = {1: _("Monday"),
            2: _("Tuesday"),
            3: _("Wednesday"),
            4: _("Thursday"),
            5: _("Friday"),
            6: _("Saturday"),
            7: _("Sunday"), }
    DAYS_SHORT = {1: _("Mo"),  # _("Lun"),
                  2: _("Tu"),  # _("Mar"),
                  3: _("We"),  # _("Mer"),
                  4: _("Th"),  # _("Jeu"),
                  5: _("Fr"),  # _("Ven"),
                  6: _("Sa"),  # _("Sam"),
                  7: _("Su"),  # _("Dim"),
                  }
    CHOICES = [(idx, value) for idx, value in DAYS.items()]

    @staticmethod
    def summary_from_list(tab, empty=' '):
        if tab is None:
            return '-'.join([empty for a in range(len(DaysOfWeek.DAYS))])
        return '-'.join([str(DaysOfWeek.DAYS_SHORT.get(i, empty)) for i in tab])


class DaysFormField(forms.TypedMultipleChoiceField):
    # different widget, comment to change interface:
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        if 'max_length' in kwargs:
            kwargs.pop('max_length')
        kwargs['choices'] = DaysOfWeek.CHOICES
        super().__init__(*args, **kwargs)


class DaysField(models.CharField):
    description = _("Comma-separated integers between 1 and 7")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 13  # max. len = all days = "1,2,3,4,5,6,7" = 13
        super().__init__(*args, **kwargs)

    @staticmethod
    def value_to_array(value):
        if value is None:
            return None
        try:
            if isinstance(value, list):
                return [int(a) for a in value]
            elif isinstance(value, str):
                return [int(a) for a in value.split(',')]
        except (TypeError, ValueError):
            raise ValidationError(_("Unexpected value"))
        raise ValidationError(_("Unexpected value"))

    @staticmethod
    def from_db_value(value, expression, connection):
        return DaysField.value_to_array(value)

    def to_python(self, value):
        return DaysField.value_to_array(value)

    def get_prep_value(self, value):
        return ','.join([str(a) for a in value]) if value is not None else None

    def formfield(self, **kwargs):
        # ignore the admin directives: directly override with our custom form:
        return super().formfield(form_class=DaysFormField,
                                 initial=[])

    # region - Validator -
    class ListBetween1And7Validator:

        def __call__(self, value):
            try:
                if isinstance(value, list):
                    loop = [int(a) for a in value]
                elif isinstance(value, str):
                    loop = [int(a) for a in value.strip('[]').split(',')]
                else:
                    raise ValueError()
                for v in loop:
                    if not (7 >= v >= 1):
                        raise ValueError()
            except (TypeError, ValueError):
                raise ValidationError(
                    _("Enter a list if coma-separated values between 1 and 7."),
                    code='invalid')

    # endregion - Validator -

    default_validators = [ListBetween1And7Validator()]
