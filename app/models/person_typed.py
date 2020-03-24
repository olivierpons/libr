import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from core.models.person import Person


class PersonTyped(Person):

    class Type(models.IntegerChoices):
        SUPER_ADMIN = 1, _('Super administrator')
        CONTRIBUTOR = 2, _('Contributor')

    person_type = models.IntegerField(
        default=Type.CONTRIBUTOR, choices=Type.choices)

    def is_contributor(self):
        return self.person_type == self.Type.CONTRIBUTOR

    def is_super_admin(self):
        return self.person_type == self.Type.SUPER_ADMIN

    def __str__(self):
        return f'{self.get_person_type_display()} / {super().__str__()}'


@receiver(post_save, sender=Person)
def my_post_save_user_handler(sender, instance, created, **kwargs):
    if created:  # a Person = physical -> create the associated person_type:
        p = PersonTyped(person_ptr=instance,
                        date_creation=datetime.date.today(),
                        date_last_modif=datetime.date.today(),)
        p.save_base(raw=True)
