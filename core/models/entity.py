from django.db import models, IntegrityError
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.models.activity import Activity
from core.models.address import Address
from core.models.address_type import AddressType
from core.models.base import BaseModel

from django.utils.translation import ugettext_lazy as _

from core.models.phone import Phone


class Entity(BaseModel):
    is_physical = models.BooleanField(default=True)
    addresses = models.ManyToManyField('Address', through='EntityAddress',
                                       blank=True, related_name='entities')
    phones = models.ManyToManyField('Phone', through='EntityPhone',
                                    blank=True, related_name='entities')
    activities = models.ManyToManyField(Activity,
                                        blank=True, related_name='entities')

    def is_person(self):
        return hasattr(self, 'person')

    def as_person(self):
        return self.person if hasattr(self, 'person') else None

    def __str__(self):
        if hasattr(self, 'person'):
            return f'{self.person.simple_desc()}'
        return '? direct call ?'


class EntityAddress(BaseModel):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE,
                               blank=False, null=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                blank=False, null=False)
    address_type = models.ForeignKey(AddressType, models.CASCADE,
                                     blank=False, null=False)
    comment = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        result = f'{str(self.entity)} -> {str(self.address)} ' \
                 f'({str(self.address_type)})'
        if self.comment:  # add the comment
            return f'{result} - {str(self.comment)}'
        return result

    class Meta:
        verbose_name = _("Entity address")
        verbose_name_plural = _("Entity addresses")


class EntityPhone(BaseModel):

    class Type(models.IntegerChoices):
        MOBILE = 1, _('Mobile')
        EMERGENCY = 2, _('Emergency')
        HOME = 3, _('Home')
        WORK = 4, _('Work')

    type = models.IntegerField(default=Type.MOBILE, choices=Type.choices)

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, null=False)
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE, null=False)
    # comment might be the phone entered by the user:
    comment = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        result = f'{str(self.entity)} -> {str(self.phone)} ' \
                 f'({str(self.get_type_display())})'
        if self.comment:  # add the comment
            return f'{result} - {str(self.comment)}'
        return result


class EntityLink(BaseModel):
    # teacher <> teaching
    E_TEACHER_LEARNER = 1
    TEACHER = _("Teacher")
    LEARNER = _("Learner")

    TAB_TYPES = {
        E_TEACHER_LEARNER: {'src': TEACHER,
                            'dst': LEARNER, },
    }
    link_type = models.IntegerField(
        choices=[(a, f'{b["src"]} ↔ {b["dst"]}') for a, b in TAB_TYPES.items()],
        default=None, blank=True, null=True)
    src = models.ForeignKey(Entity, on_delete=models.CASCADE,
                            related_name='src', blank=True, null=True)
    dst = models.ForeignKey(Entity, on_delete=models.CASCADE,
                            related_name='dst', blank=True, null=True)

    def description(self, str_a, str_b, direction):
        return f'{str_a} ' \
               f'→ {self.TAB_TYPES[self.link_type][direction].lower()} ' \
               f'→ {str_b}'

    def desc(self, entity):
        # using self.src / or / self.dst forces a lookup -> to str() first:
        try:
            str_src = str(self.src)
        except Entity.DoesNotExist:  # should never happen
            str_src = '? (not found) ?'
        try:
            str_dst = str(self.dst)
        except Entity.DoesNotExist:  # should never happen
            str_dst = '? (not found) ?'
        if entity == self.src:
            return self.description(str_src, str_dst, 'src')
        return self.description(str_dst, str_src, 'dst')

    def __str__(self):
        return f'{self.pk} - {self.desc(self.src)}'  # by default

    class Meta:
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')
        # you cant have same relation between two entities twice:
        unique_together = ('src', 'dst', 'link_type')


@receiver(pre_save, sender=EntityLink)
def entity_link_pre_save(instance, *args, **kwargs):
    if EntityLink.objects.filter(src=instance.dst, dst=instance.src,
                                 link_type=instance.link_type).count() > 0:
        raise IntegrityError(_("There's already an opposite link like that"))
    return instance
