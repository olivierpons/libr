import glob
import os
from os import path
from pathlib import Path

import cv2
import numpy
from PIL import Image
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from core.models.file.image import ImageFile
from libr.settings import MEDIA_ROOT, UPLOAD_FOLDER_IMAGES


class Command(BaseCommand):
    help = "Searching image files in a directory that are *not* jpg and" \
           "convert them to jpg (maximum quality)"

    def add_arguments(self, parser):
        default_folder_dst = UPLOAD_FOLDER_IMAGES
        parser.add_argument(
            '--continue-on-low-quality', type=int, default=1,
            help=_("If minimum quality not reached, still continue "
                   "(0=no, 1=yes), default no"))
        parser.add_argument(
            '--creator-username', type=str, required=True,
            help=_("Username to set as creator"))
        parser.add_argument(
            '--folder-src', type=str, required=True, help=_(f"Folder source"))
        parser.add_argument(
            '--folder-dst', type=str, default=default_folder_dst,
            help=_(f"Folder destination *relative* to project"
                   f" (default: {default_folder_dst})"))
        parser.add_argument(
            '--max-conversions', type=int, default=0,
            help=_("Max. conversions (default=0 = all files found)"))
        parser.add_argument(
            '--mse-max', type=int, default=30,
            help=_("Maximum acceptable Mean Squared Error "
                   "(otherwise quality is automatically increased) "
                   "(default=30)"))
        parser.add_argument(
            '--override-existing', type=int, required=True,
            help=f'If converted image already exists, override it '
                 f'(0=no, 1=yes, default:0).')
        parser.add_argument(
            '--progressive', type=bool, default=True,
            help=f'If this image should be STORED as a progressive JPEG file '
                 f'(0=no progressive, 1=progressive, default:1).')
        parser.add_argument(
            '--quality', type=int, default=100,
            help=f'Quality: 1<=quality<=100 (higher quality, bigger files)')
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
        # region - continue-on-low-quality (0=no, 1=yes), default no -
        try:
            tmp = int(options.get('continue_on_low_quality', 0))
            continue_on_low_quality = bool(tmp)
        except ValueError:
            raise CommandError(f"continue-on-low-quality option must be 0 or 1")
        # endregion - continue-on-low-quality (0=no, 1=yes), default no -
        # region - folder source -
        folder_src = Path(options.get('folder_src', '')).absolute()
        if not folder_src.exists():
            raise_error(f"Folder source \"{folder_src}\" doesn't exist.")
        if not folder_src.is_dir():
            raise_error(f"Folder source \"{folder_src}\" is not a folder.")
        # endregion - folder source -
        # region - folder destination -
        try:
            folder_dst = Path(options['folder_dst'])
        except KeyError:
            raise CommandError(_(f"Folder destination is mandatory."))
        folder_dst_full = Path(MEDIA_ROOT, folder_dst).absolute()
        if not folder_dst_full.exists():
            raise_error(_(
                f"Folder destination \"{folder_dst}\" doesn't exist."))
        if not folder_dst_full.is_dir():
            raise_error(_(
                f"Folder destination \"{folder_dst}\" is not a folder."))
        if folder_dst.is_absolute():
            raise_error(_(
                f"Folder destination \"{folder_dst}\" must be *relative*."))
        # endregion - folder destination -
        # region - out option (0=silent, 1=verbose) -

        def out_silent(msg):
            pass

        def out_verbose(msg, **kwargs):
            time = now().strftime('%Y/%m/%d %H:%M:%S')
            if not isinstance(msg, list):
                messages = [msg, ]
            else:
                messages = msg
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
        # region - override existing files (0=no, 1=yes), default: 0 -
        try:
            override_existing = int(options.get('override_existing', 0))
            override_existing = override_existing != 0
        except ValueError:
            raise CommandError(f"Override existing option must be 0 or 1.")
        # endregion - override existing files (0=no, 1=yes), default: 0 -
        # region - quality option (1..100), default: 95 -
        try:
            quality_ref = int(options.get('quality', -1))
            if not (1 <= quality_ref <= 100):
                quality_ref = 95
        except ValueError:
            raise CommandError(f"quality option must be 1 <= quality <= 100.")
        # endregion - quality option (1..100), default: 95 -
        # region - progressive option (0/1) -
        try:
            progressive = bool(int(options.get('progressive', 1)))
        except ValueError:
            raise CommandError(f"progressive option must be '0' or '1'.")
        # endregion - progressive option -
        # region - max conversions (0=all otherwise number) -
        try:
            max_conversions = int(options.get('max_conversions', 0))
            if max_conversions < 0:
                max_conversions = 0
        except ValueError:
            raise CommandError(f"max_conversions must be an integer >= 0.")
        # endregion - max conversions (0=all otherwise number) -
        # region - mse acceptable (number > 0) -
        try:
            mse_max = int(options.get('mse_max', 30))
            if mse_max <= 0:
                raise CommandError(f"mse_max must be an integer > 0.")
        except ValueError:
            raise CommandError(f"mse_max must be an integer > 0.")
        # endregion - mse acceptable (number > 0) -
        # region - output summary of selected options -
        summary = [
            f"Quality: {quality_ref}.",
            f"Folder source: \"{folder_src}\".",
            f"Folder destination: \"{folder_dst}\".",
            f"Folder destination full: \"{folder_dst_full}\".",
            f"Progressive: \"{str(progressive)}\".",
            f"Maximum acceptable Mean Squared Error: \"{str(mse_max)}\".",
            f"Continue on low quality: \"{str(continue_on_low_quality)}\"."]
        if max_conversions > 0:
            summary.append(f"Max conversions: {max_conversions}.")
        else:
            summary.append('Max conversions = 0 -> converting all files found')
        out(summary, is_success=True)
        out(["Remember:",
             "- as the MSE *increases* the images are less similar "
             "(0.0 = perfect),",
             "- as the SSIM *decreases* the images are less similar "
             "(1.0 = perfect),"], is_warning=True, without_time=True)
        # endregion - output summary of selected options -

        files_grabbed = []
        for f in ['*.gif', '*.png']:
            # ! '**' means "between folder and filename: zero or more
            #        (= recursive!) sub-folders":
            files_grabbed += glob.glob(path.join(folder_src, '**', f),
                                       recursive=True)
        total_len = len(files_grabbed)
        if max_conversions > 0:
            out(f"{total_len} file(s). Processing {max_conversions} file(s).",
                is_success=True)
            total_len = max_conversions
        else:
            out(f"{total_len} file(s). Processing all files", is_success=True)

        dst_absolute = Path(MEDIA_ROOT).absolute()

        for idx, filename_src in enumerate(files_grabbed):

            if 0 < max_conversions == idx:
                out(f"All files processed. Stopping.", is_success=True)
                break

            out(f"Processing file {idx+1}/{total_len}...")
            filename_dst = Path(
                folder_dst_full,
                Path(filename_src).parent.relative_to(folder_src),
                path.basename(path.splitext(filename_src)[0])+'.jpg')
            try:
                os.makedirs(Path(filename_dst).parent)
            except FileExistsError:
                pass
            out([f"Converting "
                 f"\"{filename_dst.relative_to(folder_dst_full)}\"..."])

            if filename_dst.is_file():
                message = _("File already exists. ")
                if not override_existing:
                    out(message + f"Override option off, skipping.",
                        is_warning=True)
                    continue
                out(message + f"Override option on, overriding.",
                    is_warning=True)

            image = Image.open(filename_src)
            rgb_img = image.convert('RGB')
            quality = quality_ref

            img_src = cv2.imread(filename_src)

            while True:
                rgb_img.save(str(filename_dst), quality=quality,
                             progressive=progressive)
                img_dst = cv2.imread(str(filename_dst))

                # Compute 'Mean Squared Error': it's the sum of the squared
                # difference between the two images.
                # The lower the error, the more "similar" the two images are.
                # NOTE: the two images must have the same dimension.
                mse = numpy.sum((img_src.astype("float") -
                                 img_dst.astype("float")) ** 2)
                mse /= float(img_src.shape[0] * img_src.shape[1])

                # # Compute  structural similarity:
                # from skimage.metrics import structural_similarity
                # s_s = structural_similarity(img_src, img_dst,
                #                             multichannel=True)
                # result = "MSE: {:.2f}, SSIM: {:.2f}".format(mse, s_s)
                result = f"MSE: {mse:.2f}"
                if mse > mse_max:
                    # Similarity is not acceptable:
                    message = f"{result}, MSE > mse_max ({mse_max:.2f})."
                    if quality == 100:
                        if continue_on_low_quality:
                            out([message,
                                 "Max quality reached. "
                                 "continue-on-low-quality option is On. "
                                 "Not stopping, next file."], is_warning=True)
                            break
                        raise CommandError("Max quality reached. "
                                           "Still not Ok. Stopping.")
                    # find the right increment (after to 90 = 1 by 1):
                    for limits, q_step in {(0, 80): 5,
                                           (81, 90): 2,
                                           (91, 100): 1, }.items():
                        if limits[0] <= quality <= limits[1]:
                            quality += q_step
                    quality = min(quality, 100)
                    out(message + f" Increasing quality to {quality}")
                else:
                    out(f"{result}, it's acceptable. Conversion done.",
                        is_success=True)
                    filename_rel = str(filename_dst.relative_to(dst_absolute))
                    try:
                        image = ImageFile.objects.filter(
                            Q(image_file=str(filename_dst)) |
                            Q(image_file=filename_rel))
                        if len(image) > 1:
                            for i in range(1, len(image)):
                                image[i].delete()
                        elif len(image) == 1:
                            image = image[0]
                        else:
                            image = ImageFile(image_file=filename_rel)
                    except ImageFile.DoesNotExist:
                        image = ImageFile(image_file=filename_rel)

                    image.original_filename = str(filename_src)
                    image.creator = creator
                    image.informations = f"Mean Squared Error: {mse:.2f}"
                    image.save()
                    break
            out("File \"{}\" processed. ({:0.4}% done)".format(
                filename_dst.relative_to(dst_absolute),
                (idx+1)*100/total_len
            ), is_success=True)

        out(f"Job finished.", is_success=True)
