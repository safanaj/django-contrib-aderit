# -*- coding: utf-8 python-indent: 4 -*-
# vim: set fileencoding=utf-8 :

# Django settings for @PROJECT@ project.
import os

gettext = lambda s: s

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_NAME = os.path.basename(PROJECT_PATH)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': os.path.join(PROJECT_PATH, '%s.db' % '@PROJECT@'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'it'
LANGUAGES = [('it', 'Italian'), ('en', 'English')]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static_collected')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = os.path.join(STATIC_URL,'admin/')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.    

    # decommnet below line after './run.sh collectstatic' to override static files
    #os.path.join(PROJECT_PATH, '%s_static' % PROJECT_NAME.lower()),
    os.path.join(PROJECT_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@SECRET@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #'django.middleware.locale.LocaleMiddleware',
    #'django.contrib.aderit.generic_utils.middleware.SessionBasedLocaleMiddleware',
    #'django.contrib.aderit.generic_utils.middleware.LocalUserMiddleware',
    #'django.contrib.aderit.generic_utils.middleware.MobileDetectionMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
)

ROOT_URLCONF = '%s.urls' % PROJECT_NAME

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = '%s.wsgi.application' % PROJECT_NAME

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, '%s_templates' % PROJECT_NAME.lower()),
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.markup',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.webdesign',
    'django_extensions',
    'south',

    #'dajax',
    #'dajaxice',
    
    'django.contrib.aderit.generic_utils',
    'django.contrib.aderit.send_mail',
    #'captcha',
    #'django.contrib.aderit.access_account',
    'account',
)

# Some frequent used settings
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#SESSION_COOKIE_AGE = 3600
#SESSION_SAVE_EVERY_REQUEST = True
LOGIN_URL = "/access"
#LOGIN_REDIRECT_URL
#ACCESS_ACCOUNT_USE_CAPTCHA = False

AUTH_PROFILE_MODULE = 'account.Account'

#DAJAXICE_MEDIA_PREFIX="dajaxice"

#CAPTCHA_FONT_SIZE = 50

# EMAIL_HOST = 'localhost'
# SEND_MAIL_ON_ACQUIRE = False
# SEND_MAIL_ON_ACQUIRE_TYPE_NAME = 'onacquire'
# SEND_MAIL_ON_LOGIN = False
# SEND_MAIL_ON_LOGIN_TYPE_NAME = 'onlogin'
# SEND_MAIL_ON_CHARGE = False
# SEND_MAIL_ON_CHARGE_TYPE_NAME = 'oncharge'
# SEND_MAIL_ON_SIGNUP = False
# SEND_MAIL_ON_SIGNUP_TYPE_NAME = 'onsignup'
# SEND_MAIL_TO_ADMIN_ON_SIGNUP = False
# SEND_MAIL_ON_SIGNUP_TO_ADMIN_TYPE_NAME = 'onsignup2admin'

# Variabili per logging #####################################
_LOG_VERBOSE_FORMAT = '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
_LOG_SIMPLE_FORMAT = '%(asctime)s %(name)s:%(levelname)s:%(lineno)d: %(message)s'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
            }
        },
    'formatters': {
        'verbose': {
            'format': _LOG_VERBOSE_FORMAT
            },
        'simple': {
            'format': _LOG_SIMPLE_FORMAT
            },
        },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
            },
        'console': {'class': 'logging.StreamHandler'},
        'syslog': {'class': 'logging.handlers.SysLogHandler'},
        'filelog': {'class': 'logging.FileHandler', 'level':'ERROR',
                    'filename': '/var/log/django/%s/error.log' % PROJECT_NAME.lower(),
                    'formatter': 'simple'},
        'account': {'class': 'logging.FileHandler',
                    'filename': '/var/log/django/%s/account.log' % PROJECT_NAME.lower(),
                    'formatter': 'simple'},
        'aderit': {'class': 'logging.FileHandler',
                   'filename': '/var/log/django/%s/aderit.log' % PROJECT_NAME.lower(),
                   'formatter': 'simple'},
        'debug': {'class': 'logging.FileHandler', 'level':'DEBUG',
                  'filename': '/var/log/django/%s/debug.log' % PROJECT_NAME.lower(),
                  'formatter': 'simple'},
        },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        
        'django.db.backends':{'handlers': ['console', 'syslog'], 'level':'INFO', 'propagate':True},
        'django.console':{'handlers': ['console'], 'level':'INFO', 'propagate':True},
        'django.syslog':{'handlers': ['syslog'], 'level':'INFO', 'propagate':True},
        'django.console.debug':{'handlers': ['console'], 'level':'DEBUG', 'propagate':True},
        'django.syslog.debug':{'handlers': ['syslog'], 'level':'DEBUG', 'propagate':True},
        'django.debug':{'handlers': ['console', 'syslog', 'debug'],
                        'level':'DEBUG', 'propagate':True},
        'account':{'handlers': ['filelog', 'debug', 'account'], 'level':'DEBUG', 'propagate':True},
        'aderit':{'handlers': ['filelog', 'debug', 'aderit'], 'level':'DEBUG', 'propagate':True},
        }
}

### other settings to override

try:
    from db_settings import *
except ImportError:
    pass

try:
    from cms_settings import *
except ImportError:
    pass

try:
    from local_settings import *
except ImportError:
    pass

