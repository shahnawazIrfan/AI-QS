from .base import *

#==================================================DEBUG Settings==================================================
DEBUG = False

#==================================================Allowed Host==================================================

ALLOWED_HOSTS = [
    'portal.ai-qs.io',
    'ai-qs-env.eba-yphnswrv.eu-west-2.elasticbeanstalk.com'
]

#==================================================Database=================================================

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'aiqs',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://syedminhaj65:ZXC!asd123@cluster0.sm0jc.mongodb.net/aiqs',
            'tls': True,
        }
    }
}

#==================================================Middlewares==================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

#==================================================Static Files Settings==================================================

STATIC_URL = "/static/"
STATIC_ROOT = "static/"

#==================================================Internationalization==================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/London'

#==================================================Rest Framework Settings==================================================

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}