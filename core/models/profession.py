from django.db import models
from django.utils.functional import cached_property

from core.models.activity import Activity
from core.models.activity_type import ActivityType


class ProfessionManager(models.Manager):
    @cached_property
    def activity_type_profession(self):
        try:
            return ActivityType.objects.get(name=ActivityType.PROFESSION_TYPE)
        # except ActivityType.DoesNotExist:
        #     return None
        # It's ugly, but when doing migrations if ActivityType is not created
        # there's an exception only known by psycopg2...
        # -> uncomment this instead for the time of migrations *ONLY*:
        except:
            return None

    def get_queryset(self):
        return super().get_queryset().filter(
            activity_type=self.activity_type_profession)


class Profession(Activity):
    class Meta:
        proxy = True

    objects = ProfessionManager()

    def __str__(self):
        return f'{self.str_clean(self.name)}'

    # region - DOCTOOME utilities -
    # add this
    DOCTOOME_TABLE = {
        'podologue': 'p10',  # Podiatrist
        'orthophoniste': 'p12',  # Speech_therapist
        'infirmière': 'p2',  # Nurse
        'médecin': 'p3',  # Gp
        'orthoptiste': 'p31',  # Orthoptic
        'psycho': 'p71',  # Psychologist
        'ergothérapeute': 'p77',  # Occupational_therapist
        'ostéopathe': 'p93',  # Osteopath
        'kinésithérapeute': 'p95',  # Physiotherapist
        'sage-femme': 'p96',  # Midwife
    }

    @staticmethod
    def doctoome_key_from_profession(profession):
        """
        connect doctoome profession codes with visitadom professions names
        :param profession: string Profession name
        :return: string doctoome profession code (or '' if not found)
        """
        profession = profession.lower()
        try:
            return Profession.DOCTOOME_TABLE[profession]
        except KeyError:
            return ''
    # endregion - DOCTOOME -
