import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o1w0yb+u%28@usp6$97^7oa#g=^*voo2inf6b)w&8g-u+z4!c)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
    'app.apps.AppConfig',
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
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

DJANGO_AUTH_VALIDATION = 'django.contrib.auth.password_validation'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': f'{DJANGO_AUTH_VALIDATION}.UserAttributeSimilarityValidator', },
    {'NAME': f'{DJANGO_AUTH_VALIDATION}.MinimumLengthValidator', },
    {'NAME': f'{DJANGO_AUTH_VALIDATION}.CommonPasswordValidator', },
    {'NAME': f'{DJANGO_AUTH_VALIDATION}.NumericPasswordValidator', },
]


LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# custom settings (to put in an external file)
MEDIA_ROOT = './uploads'
THUMBNAIL_SUBDIRECTORY = 'th'
UPLOAD_FOLDER_CHATS_DOCUMENT = 'chats/documents'
UPLOAD_FOLDER_DOCUMENTS = 'documents'
UPLOAD_FOLDER_IMAGES = 'images'
THUMBNAIL_DIMENSIONS = (1125, 2436)  # iPhone X resolution
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# region -- geometry constants --
GEOMETRY_DEFAULT_SRID = 4326
GEOMETRY_ALLOWED_SRID = [4326, 3857]
# endregion

# region -- phones constants --
PHONE_ACCEPTED_FORMAT = 'FR'
# endregion

STATIC_URL = '/static/'
