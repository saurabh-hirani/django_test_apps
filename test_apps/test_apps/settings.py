"""
Django settings for test_apps project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = BASE_DIR


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p+=5d#80h7+eiq_tt&6$v%dh!7oco^u3wn8nou+7gac_(wn8n6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = [
    os.path.join(PROJECT_DIR, 'templates'),
]

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'polls',
    'blogs',
    'session_security',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'session_security.middleware.SessionSecurityMiddleware'
)

ROOT_URLCONF = 'test_apps.urls'

WSGI_APPLICATION = 'test_apps.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'storage.db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

LOGIN_URL = '/accounts/login/'
USER_HOME_URL = '/accounts/loggedin/'
LOGIN_REDIRECT_URL = USER_HOME_URL

STATICFILES_DIRS = (
  PROJECT_DIR + '/static/',
)

STATICFILES_FINDERS = (
  "django.contrib.staticfiles.finders.FileSystemFinder",
  "django.contrib.staticfiles.finders.AppDirectoriesFinder"
)

TEMPLATE_CONTEXT_PROCESSORS = (
 "django.contrib.auth.context_processors.auth",
 "django.core.context_processors.debug",
 "django.core.context_processors.i18n",
 "django.core.context_processors.media",
 "django.core.context_processors.static",
 "django.core.context_processors.tz",
 "django.contrib.messages.context_processors.messages",
 "django.core.context_processors.request",
)

SESSION_SECURITY_WARN_AFTER = 600
SESSION_SECURITY_EXPIRE_AFTER = 1200
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
