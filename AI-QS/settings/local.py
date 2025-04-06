from .base import *
import tempfile
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#==================================================Hosts==================================================

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost"
]

#==================================================Database=================================================

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'aiqs-dev',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://syedminhaj65:ZXC!asd123@cluster0.sm0jc.mongodb.net/aiqs-dev',
            'tls': True,
        }
    }
}

#==================================================Static Files directory==================================================

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/'),
]

#==================================================Internationalization==================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dubai'

#==================================================Rest Framework Settings==================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}