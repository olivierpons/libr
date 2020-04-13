import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from ast import literal_eval

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

ALLOWED_HOSTS = []


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


def str_parser(error_message_if_doesnt_exist):
    return [str, lambda v: (settings['DEBUG'] is True) or Path(v).is_dir(),
            error_message_if_doesnt_exist]


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
        'parser': str_parser("Production folder doesn't exist.")},
    'COMPRESS_ROOT': {
        'default': '../production_static_files/compress',
        'parser': str_parser("Compress production folder doesn't exist.")},
    # when set to None = no limit to be able to send huge amount of data:
    'DATA_UPLOAD_MAX_NUMBER_FIELDS': {
        'required': True,
        'parser': [eval, lambda v: v is None or isinstance(v, int)]},
    # for uploads
    'UPLOAD_FOLDER_DOCUMENTS': {'default': 'documents'},
    'UPLOAD_FOLDER_CHATS_DOCUMENT': {'default': 'chats/documents'},
    'UPLOAD_FOLDER_IMAGES': {'default': 'images'},
    'THUMBNAIL_SUBDIRECTORY': {'default': 'th'},
    'THUMBNAIL_DIMENSIONS': {
        'default': '(1125, 2436)',  # iPhone X resolution
        'parser': [eval, lambda v: (type(v) is tuple) and len(v) == 2]},
    'ALLOWED_HOSTS': {
        'default': '[]', 'required': True,  # default = no hosts
        'parser': [eval,
                   lambda tab: isinstance(tab, list) and all([
                       isinstance(x, str) for x in tab])]},  # ! array of str

    # DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2' :
    # 'ENGINE': 'django.db.backends.sqlite3',
    # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    'DATABASE_ENGINE': {'default': 'django.db.backends.sqlite3', },
    'DATABASE_NAME': {'default': os.path.join(BASE_DIR, 'db.sqlite3'), },

    'DATABASE_HOST': conf_ignore_if_sqlite(),
    'DATABASE_CLIENT_ENCODING': conf_ignore_if_sqlite(),
    'DATABASE_DATABASE': conf_ignore_if_sqlite(),
    'DATABASE_USER': conf_ignore_if_sqlite(),
    'DATABASE_PASSWORD': conf_ignore_if_sqlite(),
})

for var, infos in environment_variables.items():
    if var in os.environ:
        settings[var] = os.environ[var]
    elif 'default' in infos:
        settings[var] = infos['default']
    elif 'required' in infos:
        errors.append(var)
        continue
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

if len(errors):
    raise Exception("Please set the environment variables: "
                    "{}.".format(', '.join(errors)))

MEDIA_ROOT = settings['MEDIA_ROOT']
COMPRESS_ROOT = settings['COMPRESS_ROOT']
SECRET_KEY = settings['SECRET_KEY']
DEBUG = settings['DEBUG']
DATA_UPLOAD_MAX_NUMBER_FIELDS = settings['DATA_UPLOAD_MAX_NUMBER_FIELDS']
UPLOAD_FOLDER_DOCUMENTS = settings['UPLOAD_FOLDER_DOCUMENTS']
UPLOAD_FOLDER_CHATS_DOCUMENT = settings['UPLOAD_FOLDER_CHATS_DOCUMENT']
UPLOAD_FOLDER_IMAGES = settings['UPLOAD_FOLDER_IMAGES']
THUMBNAIL_SUBDIRECTORY = settings['THUMBNAIL_SUBDIRECTORY']
THUMBNAIL_DIMENSIONS = settings['THUMBNAIL_DIMENSIONS']
ALLOWED_HOSTS = settings['ALLOWED_HOSTS']
STATIC_ROOT = settings['STATIC_ROOT']

# endregion - custom settings (to put in environment settings) -

# Application definition

INSTALLED_APPS = [
    'core.apps.CoreConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'app.apps.AppConfig', short='app' otherwise PyCharm = problem with paths:
    'app',
]

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

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = 'libr.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
PASSWORD_VALIDATION = 'django.contrib.auth.password_validation'
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

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('app_index')
