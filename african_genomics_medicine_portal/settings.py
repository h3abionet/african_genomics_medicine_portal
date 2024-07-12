"""
Django settings for african_genomics_medicine_portal project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
# as a failsafe if you don't have this flag in config switch on production
DEBUG = config.DEBUG

ALLOWED_HOSTS = [
    '85.159.209.149','137.158.204.58',
    'localhost',
    '127.0.0.1',
    'agmp.h3abionet.org',
    'dockerhost02.cbio.uct.ac.za',
]

ADMIN_URL = "madiba/"

# Application definition

AGNOCOMPLETE_DATA_ATTRIBUTE = 'autocomplete'

INSTALLED_APPS = [
    'bootstrap4',
    'crispy_forms',
    'agmp_app',
    'leaflet',
    'agnocomplete',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    'dal_select2',
]

SHELL_PLUS = "notebook"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'african_genomics_medicine_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'african_genomics_medicine_portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# new Django 3.2
# https://dev.to/weplayinternet/upgrading-to-django-3-2-and-fixing-defaultautofield-warnings-518n

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
# os.path.abspath("static")  # added by Anmol
CRISPY_TEMPLATE_PACK = 'bootstrap4'
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_cdn')

# if not DEBUG:
#     STATIC_ROOT = "/var/www/static/"

# print(BASE_DIR)
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static')
#     # "/home/devil/Documents/Tools/Database/staticfiles"
# ]

RESULTS_PER_PAGE = 50

LEAFLET_CONFIG = {
    'TILES': [('Streets', 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}{r}.png',
               {
                   'attribution': '&copy; Data from H3ABioNet',
                   'lang': 'en'
               })]
}


# cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # In-memory cache for development
        # For production, use 'django_redis.cache.RedisCache' or 'django.core.cache.backends.memcached.MemcachedCache'
        'LOCATION': 'unique-snowflake',
    }
}

