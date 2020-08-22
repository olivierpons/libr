from django.conf import settings

from .document import DocumentFile


class ChatDocument(DocumentFile):
    upload_directory = settings.UPLOAD_FOLDER_CHATS_DOCUMENT
