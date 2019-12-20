import uuid
from random import randint

from django.utils.datetime_safe import datetime as datetime_safe


class UidMixin(object):
    @staticmethod
    def generate_uid(text_to_append='', salt=''):
        # pris ici : http://stackoverflow.com/questions/
        # 6999726/how-can-i-convert-a-datetime-object-to
        # -milliseconds-since-epoch-unix-time-in-p
        #
        epoch = datetime_safe.utcfromtimestamp(0)

        def millis(dt):
            return (dt - epoch).total_seconds() * 1000.0

        nom = str(randint(0, 90000000) + int(millis(datetime_safe.now())))
        return str(uuid.uuid5(uuid.NAMESPACE_OID, nom + salt)) + text_to_append
