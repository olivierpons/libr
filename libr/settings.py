import ipaddress
import os
import re
from pathlib import Path
from django.urls import reverse_lazy
from socket import gethostname, gethostbyname, gethostbyname_ex

from collections.abc import Mapping

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# region - custom settings (to put in environment settings) -
class LazyDict(Mapping):
    def __init__(self, *args, **kw):
        self._raw_dict = dict(*args, **kw)

    def __getitem__(self, key):
        if key.startswith('#'):
            func, arg = self._raw_dict.__getitem__(key)
            return func(arg)
        return self._raw_dict.__getitem__(key)

    def __iter__(self):
        return iter(self._raw_dict)

    def __len__(self):
        return len(self._raw_dict)


settings = {}
errors = []


def dir_parser(error_message_if_doesnt_exist):
    return [str, lambda v: (settings['DEBUG'] is True) or Path(v).is_dir(),
            error_message_if_doesnt_exist]


def parser_array_of_str(error_message):
    return [eval,
            lambda tab: (isinstance(tab, list) or isinstance(tab, tuple))
                        and all([isinstance(x, str) for x in tab]),
            error_message]  # ! array of str


def conf_ignore_if_sqlite():
    return {
        'default': 'None',
        'parser': [eval,
                   lambda v:
                   (isinstance(v, str) and v != '') or
                   (v is None and 'sqlite' in settings['DATABASE_ENGINE']),
                   "Your database isn't sqlite, this var must be configured"]}


environment_variables = LazyDict({
    # SECURITY WARNING: don't run with debug turned on in production!
    'DEBUG': {'required': True,
              'parser': [eval, lambda v: isinstance(v, bool)]},
    'SECRET_KEY': {'required': True, },
    'MEDIA_ROOT': {'default': 'uploads'},
    'STATIC_ROOT': {
        'default': '../production_static_files',
        'parser': dir_parser("Production folder doesn't exist.")},
    'COMPRESS_ROOT': {
        'default': '../production_static_files/compress',
        'parser': dir_parser("Compress production folder doesn't exist.")},
    # when set to None = no limit to be able to send huge amount of data:
    'DATA_UPLOAD_MAX_NUMBER_FIELDS': {
        'required': True,
        'parser': [eval, lambda v: v is None or isinstance(v, int)]},
    # for uploads
    'UPLOAD_FOLDER_DOCUMENTS': {'default': 'documents'},
    'UPLOAD_FOLDER_MUSICS': {'default': 'musics'},
    'UPLOAD_FOLDER_CHATS_DOCUMENT': {'default': 'chats/documents'},
    'UPLOAD_FOLDER_IMAGES': {'default': 'images'},
    'THUMBNAIL_SUBDIRECTORY': {'default': 'th'},
    'THUMBNAIL_DIMENSIONS': {
        'default': '(1125, 2436)',  # iPhone X resolution
        'parser': [eval, lambda v: (type(v) is tuple) and len(v) == 2]},

    # https://docs.djangoproject.com/en/dev/ref/settings/
    'ALLOWED_HOSTS': {
        'default': '[]', 'required': True,  # default = no hosts
        'parser': parser_array_of_str("ALLOWED_HOSTS = list of str only!")},
    'INTERNAL_IPS': {
        'default': '["127.0.0.1", ]', 'required': True,
        'parser': parser_array_of_str("INTERNAL_IPS = list of str only!")},

    # 'DATABASE_ENGINE' = 'django.db.backends.postgresql_psycopg2',
    'DATABASE_ENGINE': {'default': 'django.db.backends.sqlite3', },
    'DATABASE_NAME': {'default': os.path.join(BASE_DIR, 'db.sqlite3'), },
    'DATABASE_HOST': conf_ignore_if_sqlite(),
    'DATABASE_CLIENT_ENCODING': conf_ignore_if_sqlite(),
    'DATABASE_DATABASE': conf_ignore_if_sqlite(),
    'DATABASE_USER': conf_ignore_if_sqlite(),
    'DATABASE_PASSWORD': conf_ignore_if_sqlite(),
})


def parse_var(var, infos):
    global settings
    if var in os.environ:
        settings[var] = os.environ[var]
    elif 'default' in infos:
        settings[var] = infos['default']
    elif 'required' in infos:
        errors.append(var)
        return
    if 'parser' in infos:
        parser = infos['parser']
        if var not in settings:
            raise Exception(f"{var}: variable not set in environment, and "
                            "has not 'default' or 'required' value")
        # ! parser functions: 0 = convert, 1 = validate conversion, 2 = error:
        try:
            settings[var] = parser[0](settings[var])
        except TypeError:
            raise Exception(f"{var}: conversion error using {parser[0]}")

        if not parser[1](settings[var]):  # should not continue -> exception:
            if len(parser) > 2:
                raise Exception(f'{var=} : {parser[2]}')
            raise Exception(f'Unexpected conversion for variable {var}')


# first parse debug then *AFTER* parse all other variables
for var, infos in environment_variables.items():
    if var == 'DEBUG':
        parse_var(var, infos)

for var, infos in environment_variables.items():
    if var != 'DEBUG':
        parse_var(var, infos)

if len(errors):
    raise Exception("Please set the environment variables: "
                    "{}.".format(', '.join(errors)))

MEDIA_ROOT = settings['MEDIA_ROOT']
COMPRESS_ROOT = settings['COMPRESS_ROOT']
SECRET_KEY = settings['SECRET_KEY']
DEBUG = settings['DEBUG']
DATA_UPLOAD_MAX_NUMBER_FIELDS = settings['DATA_UPLOAD_MAX_NUMBER_FIELDS']
UPLOAD_FOLDER_DOCUMENTS = settings['UPLOAD_FOLDER_DOCUMENTS']
UPLOAD_FOLDER_MUSICS = settings['UPLOAD_FOLDER_MUSICS']
UPLOAD_FOLDER_CHATS_DOCUMENT = settings['UPLOAD_FOLDER_CHATS_DOCUMENT']
UPLOAD_FOLDER_IMAGES = settings['UPLOAD_FOLDER_IMAGES']
THUMBNAIL_SUBDIRECTORY = settings['THUMBNAIL_SUBDIRECTORY']
THUMBNAIL_DIMENSIONS = settings['THUMBNAIL_DIMENSIONS']
ALLOWED_HOSTS = settings['ALLOWED_HOSTS']
INTERNAL_IPS = settings['INTERNAL_IPS']
STATIC_ROOT = settings['STATIC_ROOT']
# LOCALE_PATHS = settings['LOCALE_PATHS']

# endregion - custom settings (to put in environment settings) -

# https://stackoverflow.com/a/40665906/106140
ALLOWED_HOSTS = tuple(ALLOWED_HOSTS) + tuple([
    gethostname(), '127.0.0.1', '.ngrok.io',
]) + tuple(gethostbyname_ex(gethostname())[2])

DATA_UPLOAD_MAX_MEMORY_SIZE = None

if DEBUG:
    WEBSITE_NAME = 'libr.hqf.fr'
    ALLOWED_HOSTS += (WEBSITE_NAME,)
    # add my (own) company HQF for debugging purposes:
    to_add = []
    for e in ['com', 'fr']:
        for h in ALLOWED_HOSTS:
            try:
                ipaddress.ip_address(h)
            except ValueError:  # add only *not* IP's like '':
                without_ext = '.'.join(h.split('.')[:-1])
                if without_ext and '.hqf' not in without_ext:
                    to_add.append('{}.hqf.{}'.format(without_ext, e))
    if len(to_add):
        ALLOWED_HOSTS += tuple(to_add)
    # add everything on port 8000:
    for i in range(8000, 8003):
        ALLOWED_HOSTS += tuple([f'{a}:{i}' for a in ALLOWED_HOSTS])
        INTERNAL_IPS += tuple([f'{a}:{i}' for a in INTERNAL_IPS])
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    WEBSITE_NAME = 'libr.com'
    # specific to mc-media
    ALLOWED_HOSTS += ('.mc-media.com', '.libr.com', )
    SECURE_HSTS_SECONDS = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True

SERVER_EMAIL = f'root@{WEBSITE_NAME}'

ALLOWED_HOSTS = tuple(set(ALLOWED_HOSTS))
IGNORABLE_404_URLS = (
    re.compile(r'\.(php|cgi)$'),
    re.compile(r'.*phpmyadmin.*'),
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
)

ADMINS = (
    ('Olivier Pons', 'olivier.pons@gmail.com'),
)

# hard-coded, no need to set it for *each* environment:
ADMIN_JS_JQUERY = 'vendors/jquery-3.5.1.min.js'
ADMIN_JS_COLLAPSED_STACKED_INLINES = 'js/admin/collapsed_stacked_inlines.js'
ADMIN_JS_BIG_SELECT_MULTIPLES = 'js/admin/big_select_multiples.js'
ADMIN_JS_RESIZE_WIDGETS = 'js/admin/resize_widgets.js'

# Application definition

INSTALLED_APPS = [
    'core.apps.CoreConfig',
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    'app.apps.MyAdminConfig',
    'app.apps.AppConfig',  # (if PyCharm = problem with paths, change to 'app')
]

# Custom Widget with *custom* template dir:
# - add 'django.forms' in INSTALLED_APPS
# - add FORM_RENDERER below
# https://stackoverflow.com/questions/45844032/
# django-templatedoesnotexist-in-case-of-a-custom-widget
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'libr.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}, ]

WSGI_APPLICATION = 'libr.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
    # 'default': {
    #     'ENGINE': settings['DATABASE_ENGINE'],
    #     'NAME': settings['DATABASE_NAME'],
    #     'HOST': settings['DATABASE_HOST'],
    #     'OPTIONS': {
    #         'client_encoding': 'UTF8',
    #         'database': settings['DATABASE_DATABASE'],
    #         'user': settings['DATABASE_USER'],
    #         'password': settings['DATABASE_PASSWORD'],
    #     },
    # }
}

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
PASSWORD_VALIDATION = 'django.contrib.auth.password_validation'
if DEBUG:
    AUTH_PASSWORD_VALIDATORS = []
else:
    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': f'{PASSWORD_VALIDATION}.UserAttributeSimilarityValidator', },
        {'NAME': f'{PASSWORD_VALIDATION}.MinimumLengthValidator', },
        {'NAME': f'{PASSWORD_VALIDATION}.CommonPasswordValidator', },
        {'NAME': f'{PASSWORD_VALIDATION}.NumericPasswordValidator', },
    ]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# region -- geometry constants --
GEOMETRY_DEFAULT_SRID = 4326
GEOMETRY_ALLOWED_SRID = [4326, 3857]
# endregion

# region -- phones constants --
PHONE_ACCEPTED_FORMAT = 'FR'
# endregion

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('app_home')
HIJACK_LOGIN_REDIRECT_URL = reverse_lazy('app_home')
HIJACK_LOGOUT_REDIRECT_URL = reverse_lazy('app_home')
IMG_NO_IMAGE_YET = 'img/no-image-yet.png'  # use: static(IMG_NO_IMAGE_YET)
# https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
APPEND_SLASH = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

"""
import logging
l = logging.getLogger(__name__)
l.debug("*" * 50)
# Setting to output database SQL queries in the console:
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    },
    # ! add this to output all log in the console (dont ask me why!):
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
}
"""
