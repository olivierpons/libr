from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.models.base import BaseModel
from core.models.chat.message import ChatMessageDestination
from core.models.person import Person


class Chat(BaseModel):

    # all persons participating
    persons = models.ManyToManyField(Person, related_name='conversations',
                                     through='ChatPerson')

    def messages_by_date(self):
        return self.messages.all().order_by('-date_last_modif')

    def persons_who_are_not(self, p):
        return self.persons.exclude(pk=p.pk)

    def messages_unread_for(self, p):
        return ChatMessageDestination.objects.filter(
            Q(message__chat=self) & Q(destination=p) &
            Q(date_read__is_null=True)).values('message')

    def messages_unread(self):
        return ChatMessageDestination.objects.filter(
            Q(chat_message__chat=self) & Q(date_read__isnull=True)).count()

    def __str__(self):
        return _("{}: {} (unread: {})").format(
            self.date_relative(self.date_creation),
            ' / '.join([self.str_clean(p.simple_desc(), max_len=20)
                        for p in self.persons.all()]),
            self.messages_unread())

    class Meta:
        ordering = ['date_creation']


class ChatPerson(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    date_expiry = models.DateTimeField(default=None,
                                       null=True,
                                       editable=True,
                                       verbose_name=_("Expiry date"),
                                       blank=True)

    def __str__(self):
        return self.person.simple_desc() if self.person else '?'
