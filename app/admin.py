from django.contrib import admin

from core.models.activity import Activity
from core.models.activity_type import ActivityType
from core.models.address import Address
from core.models.address_type import AddressType
from core.models.chat.base import Chat, ChatPerson
from core.models.chat.message import ChatMessage, ChatMessageDestination, \
    ChatMessageDocumentFile
from core.models.company import Company
from core.models.entity import EntityAddress, Entity, EntityLink, EntityPhone
from core.models.file.chat_document import ChatDocument
from core.models.file.document import DocumentFile
from core.models.file.image import ImageFile
from core.models.geo_point import GeoPoint
from core.models.link_type import LinkType
from core.models.person import PersonConfirmation, Person, \
    PersonProfession
from core.models.phone import Phone
from core.models.phone_type import PhoneType
from core.models.profession import Profession
from core.models.role import Role

admin.site.register(Activity)
admin.site.register(ActivityType)
admin.site.register(Address)
admin.site.register(AddressType)
admin.site.register(Chat)
admin.site.register(ChatPerson)
admin.site.register(ChatMessage)
admin.site.register(ChatMessageDestination)
admin.site.register(ChatMessageDocumentFile)
admin.site.register(Company)
admin.site.register(EntityAddress)
admin.site.register(Entity)
admin.site.register(EntityLink)
admin.site.register(EntityPhone)
admin.site.register(ChatDocument)
admin.site.register(DocumentFile)
admin.site.register(ImageFile)
admin.site.register(GeoPoint)
admin.site.register(LinkType)
admin.site.register(PersonConfirmation)
admin.site.register(Person)
admin.site.register(PersonProfession)
admin.site.register(Phone)
admin.site.register(PhoneType)
admin.site.register(Profession)
admin.site.register(Role)
