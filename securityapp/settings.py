"""
Django settings for securityapp project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'NULL'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'channels',
    'captcha',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_email_verification',
    # 'tailwind',
    # 'theme',
    'axes',
    'accounts',
    'incidents',
]

ASGI_APPLICATION = 'securityapp.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    }
}

AUTH_USER_MODEL = 'accounts.User'

LOGIN_REDIRECT_URL = '/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'securityapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = 'securityapp.wsgi.application'

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# Login Attempts Restriction
# https://django-axes.readthedocs.io/en/latest/

# python manage.py axes_reset

AUTHENTICATION_BACKENDS = [
    # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    'axes.backends.AxesBackend',

    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
]

AXES_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_TEMPLATE = "accounts/users/login.html"

# Captcha
# https://blog.webmatrices.com/django-recaptcha-v3/#Install_and_configure_django-recaptcha_lib
# https://github.com/praekelt/django-recaptcha

RECAPTCHA_PUBLIC_KEY = '6LeRVtQcAAAAAM-ClLuYcFIz-XioQe5YcM6pL2Js'
RECAPTCHA_PRIVATE_KEY = '6LeRVtQcAAAAADjuvRFI48NW0KbEelQG-DIGTeTq'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'securityDb',
        'USER': 'josue',
        'PASSWORD': 'cuentas',

        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'securityapp.password_validation.HasUpperCaseValidator',
    },
    {
        'NAME': 'securityapp.password_validation.HasNumberValidator',
    },
    {
        'NAME': 'securityapp.password_validation.DontRepeatValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Django-Tailwind
# https://django-tailwind.readthedocs.io/en/latest/installation.html

# TAILWIND_APP_NAME = 'theme'

# INTERNAL_IPS = [
#     "127.0.0.1",
# ]

# NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# py manage.py tailwind start

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Verification Settings
# https://pypi.org/project/django-email-verification/
# https://support.google.com/accounts/answer/6010255#zippy=%2Csi-est%C3%A1-activada-la-opci%C3%B3n-acceso-de-apps-menos-seguras


def verified_callback(user):
    user.is_active = True


def email_query(User, email):
    return User.objects.get(worker__email=email)


EMAIL_QUERY = email_query

EMAIL_VERIFIED_CALLBACK = verified_callback

#EMAIL_FROM_ADDRESS = 'upcpry2021274dc@gmail.com'
#EMAIL_FROM_ADDRESS = 'jrasta305@gmail.com'

EMAIL_FROM_ADDRESS = 'upcpry2021274dc@gmail.com'
EMAIL_MAIL_SUBJECT = 'Verifica tu cuenta'
EMAIL_MAIL_HTML = 'accounts/mail_confirm_account.html'
EMAIL_MAIL_PLAIN = 'accounts/mail_confirm_account.txt'
EMAIL_TOKEN_LIFE = 60 * 60 * 24  # one day
EMAIL_PAGE_TEMPLATE = 'accounts/account_confirmation.html'
EMAIL_PAGE_DOMAIN = 'http://127.0.0.1:8000/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'upcpry2021274dc@gmail.com'
EMAIL_HOST_PASSWORD = 'UPC12345'
EMAIL_USE_TLS = True


# Password settings

PASSWORD_RESET_TIMEOUT_DAYS = 1  # Amount of days will take a token to expire
