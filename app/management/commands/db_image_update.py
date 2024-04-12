from os import path
from os.path import join
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from core.models.file.image import ImageFile


class Command(BaseCommand):
    help = "Temporary"
    default_folder_sync = path.join(settings.MEDIA_ROOT,
                                    settings.UPLOAD_FOLDER_IMAGES)
    media_root_folder = Path(default_folder_sync).resolve()

    def add_arguments(self, parser):
        parser.add_argument(
            '--creator-username', type=str, required=True,
            help=_("Username to set as creator"))
        parser.add_argument(
            '--folder-sync', type=str, default=self.default_folder_sync,
            help=_(f"Folder to sync (default: {self.default_folder_sync})"))
        parser.add_argument(
            '--max-conversions', type=int, default=0,
            help=_("Max. conversions (default=0 = all files found)"))
        parser.add_argument(
            '--mse-max', type=int, default=30,
            help=_("Maximum acceptable Mean Squared Error "
                   "(otherwise quality is automatically increased), "
                   "default=30"))
        parser.add_argument(
            '--db-remove-if-no-file', type=int, default=0,
            help=_("Database: remove record if no file found "
                   "(0=no, 1=yes), default: 0=no"))
        parser.add_argument(
            '--force-thumbnail-gen', type=int, default=0,
            help=_("For new database records, force their thumbnail generation "
                   "(0=no, 1=yes), default: 0=no"))
        parser.add_argument(
            '--verbose', type=int, default=1,
            help=_("Verbose (0=silent, 1=verbose), default: 1=verbose"))

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
        # region - folder sync -
        folder_sync = Path(options.get('folder_sync', '')).absolute()
        if not folder_sync.exists():
            raise_error(f"Folder sync \"{folder_sync}\" doesn't exist.")
        if not folder_sync.is_dir():
            raise_error(f"Folder sync \"{folder_sync}\" is not a folder.")
        # endregion - folder sync -
        # region - out option (0=silent, 1=verbose) -

        def out_silent(message, **kwargs):
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
        # region - db-remove-if-no-file (0=no, 1=yes) -
        db_remove_if_no_file = False
        try:
            db_remove_if_no_file = int(options.get('db_remove_if_no_file',
                                                   -1)) > 0
        except ValueError:
            raise_error(f"Remove record if no file found: 0 or 1 only.")
        # endregion - db-remove-if-no-file (0=no, 1=yes) -

        out('Syncing (database ImageFile() => file system)...')
        for image in ImageFile.objects.all():
            if image.creator is None:
                image.creator = creator
                out(f'{image} -> setting creator = {creator}')
                image.save()

            image_file = str(image.image_file)
            if not image_file:
                if db_remove_if_no_file:
                    out(f"ImageFile() remove option=1 -> removing empty file.")
                    image.delete()
                else:
                    out(f"ImageFile() remove option=0 -> ignoring empty file.")

            if image_file[0] == '/':
                p = Path(image_file)
            else:
                p = Path(join(folder_sync, image_file))
                if not p.is_file():
                    if image.is_path_relative:  # try with media root/image:
                        p = Path(join(self.media_root_folder, image_file))
            if p.is_file():
                try:
                    # !! FULL path (= to put them on different disks if needed):
                    image.image_file = p
                    image.save()
                    out(f"Ok for: '{p}'")
                except FileNotFoundError:
                    out(f"Error for: '{p}'")
                    if db_remove_if_no_file:
                        out(f"ImageFile(): removing '{image_file}'")
                        image.delete()
            else:
                msg = f"ImageFile(): not found: '{image_file}'"
                if db_remove_if_no_file:
                    out(f"{msg} -> remove option=1 -> removing.")
                    image.delete()
                else:
                    out(f"{msg} -> remove option=0 -> ignoring.")
            # break

        out('Syncing (database ImageFile() => file system) done.')
        out('Syncing (file system => database ImageFile())...')
        thumbnail_dir = settings.THUMBNAIL_SUBDIRECTORY
        for filename in Path(folder_sync).rglob('*'):
            if not filename.is_file():
                continue
            # Path().name = like old "basename()":
            if Path(filename).parent.name == thumbnail_dir:
                continue
            if not ImageFile.objects.filter(image_file=filename).exists():
                img = ImageFile.objects.create(
                    creator=creator,
                    informations='Created by command line db_image_update',
                    original_filename=str(filename),
                    image_file=str(filename),
                    path_relative_to_media_root=False,
                )
                img.save(force_thumbnail_gen=False)
                out(f'Created file: {filename}')

        out('Syncing (file system => database ImageFile()) done.')

        out(f"Job finished.", is_success=True)
