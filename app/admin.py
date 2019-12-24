import copy

from django.utils.translation import gettext_lazy as _
from django.contrib.admin import AdminSite

from app.models.book.page import BookPage
from app.models.book.paragraph import BookParagraph
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

from app.models.book.base import Book


# region - MyAdminSite -
class MyAdminSite(AdminSite):
    site_header = _("Administration")

    models_on_top = ['Book', 'Person', 'Address',
                     'ChatDocument', 'Practitioner', 'PractitionerRound',
                     'DocumentFile', 'ImageFile']

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        if len(app_list):
            # ! custom sort:
            el = copy.deepcopy(app_list[0])
            el['models'] = [a for a in el['models']
                            if a['object_name'] in self.models_on_top]
            app_list[0]['models'] = [
                a for a in app_list[0]['models']
                if a['object_name'] not in self.models_on_top
            ]
            el['name'] = _("Frequently needed")
            if len(app_list[0]['models']):
                app_list.insert(0, el)
            else:
                app_list[0] = el

        return app_list
# endregion - MyAdminSite -


my_admin_site = MyAdminSite(name='my_admin')

# region - app models -
my_admin_site.register(Book)
my_admin_site.register(BookPage)
my_admin_site.register(BookParagraph)
# endregion - app models -

# region - core models -
my_admin_site.register(Activity)
my_admin_site.register(ActivityType)
my_admin_site.register(Address)
my_admin_site.register(AddressType)
my_admin_site.register(Chat)
my_admin_site.register(ChatPerson)
my_admin_site.register(ChatMessage)
my_admin_site.register(ChatMessageDestination)
my_admin_site.register(ChatMessageDocumentFile)
my_admin_site.register(Company)
my_admin_site.register(EntityAddress)
my_admin_site.register(Entity)
my_admin_site.register(EntityLink)
my_admin_site.register(EntityPhone)
my_admin_site.register(ChatDocument)
my_admin_site.register(DocumentFile)
my_admin_site.register(ImageFile)
my_admin_site.register(GeoPoint)
my_admin_site.register(LinkType)
my_admin_site.register(PersonConfirmation)
my_admin_site.register(Person)
my_admin_site.register(PersonProfession)
my_admin_site.register(Phone)
my_admin_site.register(PhoneType)
my_admin_site.register(Profession)
my_admin_site.register(Role)
# endregion - core models -
