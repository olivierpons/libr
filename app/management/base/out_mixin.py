import sys

from django.core.management.base import CommandError
from django.utils.termcolors import colorize
from django.utils.timezone import now
from django.utils.translation import gettext as _


class OutMixin:
    """
    A mixin class for handling output messages in the command line interface.

    This mixin class includes several methods to handle output messages to
    stdout and stderr. It is intended to be used as a Mixin with BaseCommand,
    see Usage.

    Usage:
        class AddressesBaseCommand(OutMixin, BaseCommand):
            pass

        obj = AddressesBaseCommand()
        obj.out("Hello world")
    """

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        self.stderr = None
        self.stdout = None
        self.style = None
        self.out = self.out_verbose
        self.OUT_SUCCESS = None
        self.OUT_WARNING = None
        self.OUT_ERROR = None
        self.OUT_NOTICE = None
        super().__init__(stdout, stderr, no_color, force_color)

    @staticmethod
    def abort(err):
        """
        Writes the error message to stderr and raises a CommandError with the
        same message.

        Usage:
            OutMixin.abort("An error occurred")
            self.abort("An error occurred")
        """
        sys.stderr.write(_("[Error: {}]\n").format(err))
        raise CommandError(_(err))

    @staticmethod
    def out_silent(msg, **kwargs):
        """
        Writes the message to stderr only if 'is_error' is specified in kwargs.

        Usage:
            OutMixin.out_silent("An error occurred", is_error=True)
        """
        if bool(kwargs.get("is_error")):
            sys.stderr.write(_("[Error: {}]\n").format(msg))

    def out_verbose(self, msg, **kwargs):
        """
        Writes the message to stdout/stderr with timestamp and specified color.

        The color and stream (stdout/stderr) is determined by the kwargs.

        Args:
            msg (str or list): The message(s) to be printed. Can be a single
                               string or a list of strings.
            **kwargs: Arbitrary keyword arguments. Can be used to specify
                'is_error', 'is_success', 'is_warning' or 'without_time'.
                'is_error' (bool): If True, the message will be printed
                                   to stderr in red.
                'is_success' (bool): If True, the message will be printed
                                     to stdout in green.
                'is_warning' (bool): If True, the message will be printed
                                     to stdout in yellow.
                'without_time' (bool): If True, the timestamp will not be
                                       printed before the message.

        Usage:
            obj.out_verbose("Hello world")
            obj.out_verbose("An error occurred", is_error=True)
            obj.out_verbose("Operation successful", is_success=True)
            obj.out_verbose("This is a warning", is_warning=True)
            obj.out_verbose(["Message 1", "Message 2", "Message 3"])
            obj.out_verbose("No timestamp for this message", without_time=True)
        """
        time = now().strftime("%Y/%m/%d %H:%M:%S")
        messages = [msg] if not isinstance(msg, list) else msg
        str_time = f"> {time} : "
        output = self.stderr if kwargs.get("is_error") else self.stdout
        str_space = None

        style_dict = {
            "is_success": ("OUT_SUCCESS", self.style.SUCCESS),
            "is_warning": ("OUT_WARNING", self.style.WARNING),
            "is_error": ("OUT_ERROR", self.style.ERROR),
            "colorize": ("colorize", None),
        }
        default_style = ("OUT_NOTICE", self.style.NOTICE)

        for msg in messages:
            prefix = (
                str_space
                if str_space
                else (str_time if not kwargs.get("without_time") else "")
            )
            str_space = str_space or " " * len(str_time)
            for style_kwarg, (
                style_attr,
                default_method,
            ) in style_dict.items():
                if kwargs.get(style_kwarg):
                    if getattr(self, style_attr):
                        msg = colorize(msg, **getattr(self, style_attr))
                    else:
                        msg = (
                            default_method(msg)
                            if default_method
                            else colorize(msg, **kwargs.get(style_attr))
                        )
                    break
            else:
                if getattr(self, default_style[0]):
                    msg = colorize(msg, **getattr(self, default_style[0]))
                else:
                    msg = default_style[1](msg)
            output.write(f"{prefix}{msg}")

    def out_option_on_or_off(self, option: bool, description: str):
        """
        Writes the status of the specified option to stdout.

        Usage:
            obj = OutMixin(stdout=sys.stdout, stderr=sys.stderr)
            obj.out_option_on_or_off(True, "Option 1")

        Args:
            option: if the option is on or off
            description: the description of the option

        Returns:
            None
        """
        if option:
            self.out(_("[With option '{}']").format(description))
        else:
            self.out(_("[Without option '{}']").format(description))

    def out_success(self, msg, **kwargs):
        """
        Writes the message to stdout with 'success' style.

        This is a convenience method that automatically sets the
        'is_success' flag to True.

        Args:
            msg (str or list): The message(s) to be printed. Can be a single
                               string or a list of strings.
            **kwargs: Arbitrary keyword arguments. Any additional flags
                      for 'out_verbose'.

        Returns:
            None.

        Usage:
            obj.out_success("Operation successful")
        """
        self.out(msg, **{"is_success": True, **kwargs})

    def out_error(self, msg, **kwargs):
        """
        Writes the message to stderr with 'error' style.

        This is a convenience method that automatically sets the 'is_error'
        flag to True.

        Args:
            msg (str or list): The message(s) to be printed. Can be a single
                               string or a list of strings.
            **kwargs: Arbitrary keyword arguments. Any additional flags
                      for 'out_verbose'.

        Returns:
            None.

        Usage:
            obj.out_error("An error occurred")
        """
        self.out(msg, **{"is_error": True, **kwargs})
