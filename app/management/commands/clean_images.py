from os import path
from os.path import join
from pathlib import Path

from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

from core.models.file.image import ImageFile
from libr import settings
from libr.settings import MEDIA_ROOT, UPLOAD_FOLDER_IMAGES


class Command(BaseCommand):
    help = "Temporary"

    def add_arguments(self, parser):
        default_folder_dst = path.join(settings.MEDIA_ROOT,
                                       settings.UPLOAD_FOLDER_IMAGES)
        parser.add_argument(
            '--creator-username', type=str, required=True,
            help=_("Username to set as creator"))
        parser.add_argument(
            '--folder-src', type=str, required=True, help=_(f"Folder source"))
        parser.add_argument(
            '--folder-dst', type=str, default=default_folder_dst,
            help=_(f"Folder destination (default: {default_folder_dst})"))
        parser.add_argument(
            '--max-conversions', type=int, default=0,
            help=_("Max. conversions (default=0 = all files found)"))
        parser.add_argument(
            '--mse-max', type=int, default=30,
            help=_("Maximum acceptable Mean Squared Error "
                   "(otherwise quality is automatically increased) "
                   "(default=30)"))
        parser.add_argument(
            '--verbose', type=int, default=1,
            help=_("Verbose (0=silent, 1=verbose), default verbose"))

    def handle(self, *args, **options):
        def raise_error(err):
            raise CommandError(_(err))

        # region - creator username -
        creator_username = options['creator_username']
        try:
            creator = User.objects.get(username=creator_username).person
        except User.DoesNotExist:
            raise CommandError(f"User \"{creator_username}\" not found.")
        # endregion - creator username -
        # region - folder source -
        folder_src = Path(options.get('folder_src', '')).absolute()
        if not folder_src.exists():
            raise_error(f"Folder source \"{folder_src}\" doesn't exist.")
        if not folder_src.is_dir():
            raise_error(f"Folder source \"{folder_src}\" is not a folder.")
        # endregion - folder source -
        # region - folder destination -
        try:
            folder_dst = Path(options['folder_dst']).absolute()
        except KeyError:
            raise CommandError(_(f"Folder destination is mandatory."))
        if not folder_dst.exists():
            raise_error(_(
                f"Folder destination \"{folder_dst}\" doesn't exist."))
        if not folder_dst.is_dir():
            raise_error(_(
                f"Folder destination \"{folder_dst}\" is not a folder."))
        # endregion - folder destination -
        # region - out option (0=silent, 1=verbose) -

        def out_silent(msg):
            pass

        def out_verbose(message, **kwargs):
            time = now().strftime('%Y/%m/%d %H:%M:%S')
            if not isinstance(message, list):
                messages = [message, ]
            else:
                messages = message
            str_time = f'> {time} : '
            str_space = None
            for msg in messages:
                if str_space is None:  # first line = write time:
                    str_space = ' ' * len(str_time)
                    if bool(kwargs.get('without_time')):
                        self.stdout.write(str_space, ending='')
                    else:
                        self.stdout.write(str_time, ending='')
                else:
                    self.stdout.write(str_space, ending='')
                if bool(kwargs.get('is_success')):
                    self.stdout.write(self.style.SUCCESS(msg))
                elif bool(kwargs.get('is_warning')):
                    self.stdout.write(self.style.WARNING(msg))
                elif bool(kwargs.get('is_error')):
                    self.stdout.write(self.style.ERROR(msg))
                else:
                    self.stdout.write(self.style.NOTICE(msg))

        try:
            if int(options.get('verbose', -1)) > 0:
                out = out_verbose
            else:
                out = out_silent
        except ValueError:
            out = out_verbose
        # endregion - out option (0=silent, 1=verbose) -

        for image in ImageFile.objects.all():
            if image.creator is None:
                image.creator = creator
                image.save()
            image_file = str(image.image_file)
            if len(image_file) and image_file[0] == '/':
                p = Path(image_file)
                if p.is_file():
                    try:
                        with transaction.atomic():
                            rel = join(UPLOAD_FOLDER_IMAGES,
                                       p.relative_to(folder_dst))
                            image.image_file = rel
                            image.save()
                            print(f'Ok "{rel}"')
                    except FileNotFoundError:
                        print(f'Error on "{rel}"')

        out(f"Job finished.", is_success=True)
