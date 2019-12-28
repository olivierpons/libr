import os
from django.utils.translation import gettext_lazy as _
from ast import literal_eval

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

ALLOWED_HOSTS = []

# region -custom settings (to put in environment settings) -
environment_variables = {
    # SECURITY WARNING: don't run with debug turned on in production!
    'DEBUG': {'required': True, 'parser': bool},
    'SECRET_KEY': {'required': True, },
    'MEDIA_ROOT': {'default': 'uploads'},
    # set it to None = no limit to be able to send huge amount of data:
    'DATA_UPLOAD_MAX_NUMBER_FIELDS': {'required': True, 'parser': eval},
    # for uploads
    'UPLOAD_FOLDER_DOCUMENTS': {'default': 'documents'},
    'UPLOAD_FOLDER_CHATS_DOCUMENT': {'default': 'chats/documents'},
    'UPLOAD_FOLDER_IMAGES': {'default': 'images'},
    'THUMBNAIL_SUBDIRECTORY': {'default': 'th'},
    'THUMBNAIL_DIMENSIONS': {'default': '(1125, 2436)',   # iPhone X resolution
                             'parser': eval},
}

settings = {}
errors = []
for var, infos in environment_variables.items():
    if var in os.environ:
        settings[var] = os.environ[var]
    elif 'default' in infos:
        settings[var] = infos['default']
    elif 'required' in infos:
        errors.append(var)
        continue
    if 'parser' in infos:
        settings[var] = infos['parser'](settings[var])

if len(errors):
    raise Exception("Please set the environment variables: "
                    "{}.".format(', '.join(errors)))

MEDIA_ROOT = settings['MEDIA_ROOT']
SECRET_KEY = settings['SECRET_KEY']
DEBUG = settings['DEBUG']
DATA_UPLOAD_MAX_NUMBER_FIELDS = settings['DATA_UPLOAD_MAX_NUMBER_FIELDS']
UPLOAD_FOLDER_DOCUMENTS = settings['UPLOAD_FOLDER_DOCUMENTS']
UPLOAD_FOLDER_CHATS_DOCUMENT = settings['UPLOAD_FOLDER_CHATS_DOCUMENT']
UPLOAD_FOLDER_IMAGES = settings['UPLOAD_FOLDER_IMAGES']
THUMBNAIL_SUBDIRECTORY = settings['THUMBNAIL_SUBDIRECTORY']
THUMBNAIL_DIMENSIONS = settings['THUMBNAIL_DIMENSIONS']

# endregion -custom settings (to put in environment settings) -

# Application definition

INSTALLED_APPS = [
    'app.apps.AppConfig',
    'core.apps.CoreConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
DJANGO_AUTH_VALIDATION = 'django.contrib.auth.password_validation'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': f'{DJANGO_AUTH_VALIDATION}.UserAttributeSimilarityValidator', },
    {'NAME': f'{DJANGO_AUTH_VALIDATION}.MinimumLengthValidator', },
    {'NAME': f'{DJANGO_AUTH_VALIDATION}.CommonPasswordValidator', },
    {'NAME': f'{DJANGO_AUTH_VALIDATION}.NumericPasswordValidator', },
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
