from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.base import BaseModel
from core.models.file.chat_document import ChatDocument
from core.models.person import Person


class ChatMessage(BaseModel):
    chat = models.ForeignKey('Chat', related_name='messages',
                             on_delete=models.CASCADE)
    sender = models.ForeignKey(Person, related_name='message_sender',
                               on_delete=models.CASCADE)
    destinations = models.ManyToManyField(
        Person,
        related_name='chat_message_destinations',
        through='ChatMessageDestination')
    document_files = models.ManyToManyField(
        ChatDocument,
        related_name='chat_message_files',
        through='ChatMessageDocumentFile')
    message = models.TextField(null=True, blank=True,
                               verbose_name=_("Messages"))

    def message_summary(self):
        a = self.message
        if a:
            return (a[:85] + '&raquo;...') if len(a) > 90 else a
        return ''

    def message_to_html(self):
        return self.message.replace('\n', '<br />')

    def __str__(self):
        # ! destinations desc works except when trying to delete a destination:
        #   "MaxRecursiveDepth" exception is raised I don't know why:
        # destinations = ' / '.join(self.str_clean(dst.simple_desc(),
        #                                          max_len=20)
        #                           for dst in self.destinations.all())
        # if destinations:
        #     destinations = self.str_clean(destinations, max_len=120)
        # else:
        #     destinations = _("? no destinations ?")

        return '{} - {} - {} : "{}" - ({})'.format(
            _('Valid')
            if self.date_v_end is None
            else _('Expired: {}').format(self.date_relative(self.date_v_end)),
            self.date_creation.strftime('%Y-%m-%d %H:%M:%S'),
            self.sender.simple_desc(),
            self.message_summary(),
            self.document_files.filter(date_v_end__isnull=True).count()
        ).strip()

    class Meta:
        ordering = ['date_creation']


class ChatMessageDestination(BaseModel):
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    destination = models.ForeignKey(Person, on_delete=models.CASCADE)
    date_read = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self):
        return '{} ({})'.format(self.destination.simple_desc(email=False),
                                f'read: {self.date_relative(self.date_read)}'
                                if self.date_read else _("not read"))


class ChatMessageDocumentFile(BaseModel):
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    chat_document = models.ForeignKey(ChatDocument, on_delete=models.CASCADE)

    def __str__(self):
        result = f'{self.pk} - {str(self.chat_document)}'
        if self.date_v_end is None:
            return result
        return _("{} (expired: {})").format(
            result, self.date_relative(self.date_v_end)
        )
