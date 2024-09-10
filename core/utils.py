import uuid
from random import randint
from django.utils import timezone
from datetime import datetime
from zoneinfo import ZoneInfo


class UidMixin:
    @staticmethod
    def generate_uid(text_to_append='', salt=''):
        epoch = datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC"))

        def millis(dt):
            return (dt - epoch).total_seconds() * 1000.0

        # Use timezone.now() for timezone-aware current time
        current_time = timezone.now()

        # Generate a random number and add it to the current time in milliseconds
        nom = str(randint(0, 90000000) + int(millis(current_time)))

        # Generate a UUID using the combined string
        return str(uuid.uuid5(uuid.NAMESPACE_OID, nom + salt)) + text_to_append