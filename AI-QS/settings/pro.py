from .base import *

#==================================================DEBUG Settings==================================================
DEBUG = False

#==================================================Allowed Host==================================================

ALLOWED_HOSTS = [
    'ai-qs-env.eba-yphnswrv.eu-west-2.elasticbeanstalk.com'
]

#==================================================Database=================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'AI_QS_Database',
        'USER': 'administrator',
        'PASSWORD': 'AI_QS!9pL*X3^vW2&zRd0$8jKv',
        'HOST': 'ai-qs-db.ctiuygsq2ryo.eu-west-2.rds.amazonaws.com',
        'PORT': '5432',
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