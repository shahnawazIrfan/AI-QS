from pathlib import Path
import os
from django.urls import reverse_lazy
from dotenv import load_dotenv

#==================================================Base directory==================================================
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, 'web_app/templates')
AUTH_USER_MODEL = 'web_app.UserProfile'

#==================================================Environment====================================================
load_dotenv()
envPath = os.path.join(BASE_DIR, 'variables.env')
load_dotenv(dotenv_path=envPath)

#==================================================Secret key==================================================

SECRET_KEY = 'django-insecure-vq41*a(atu8d^m!zofcqu&zhcjvrb$z_!60uh3l+f&%n&c@j!z'

#==================================================Application definition==================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web_app',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders'
]

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

#==================================================Base Url configuration==================================================
LOGIN_URL = reverse_lazy('login_url')
LOGIN_REDIRECT_URL = reverse_lazy('user_dashboard')
LOGOUT_REDIRECT_URL = reverse_lazy('login_url')
ROOT_URLCONF = 'AI-QS.urls'

#==================================================Templates Configuration==================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'AI-QS.wsgi.application'

# ==================================================Authentication settings==================================================

AUTHENTICATION_BACKENDS = [
    'web_app.AuthenticateBackend.EmailModelBackend',
]


#==================================================Password validation==================================================

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


# ==================================================Internationalization==================================================

USE_I18N = True

USE_L10N = False

USE_TZ = True

STATIC_URL = '/static/'

#==================================================Logging Configurations==================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
            },
        },
    'loggers': {
        # Don't send invalid host error messages to ADMINS.
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}

ASGI_THREADS=1000

#==================================================Sessions==================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# ==================================================Rest Framework Settings==================================================

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

# ==================================================CORS Settings==================================================

CORS_ORIGIN_ALLOW_ALL = True