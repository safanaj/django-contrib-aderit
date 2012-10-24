# -*- coding: utf-8 python-indent: 4 -*-
# vim: set fileencoding=utf-8 :

# Django settings for @PROJECT@ project.
import os, sys

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
        'NAME': os.path.join(PROJECT_PATH, '%s.db' % PROJECT_NAME), # Or path to database file if using sqlite3.
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
LANGUAGES = [('it', 'Italian'),]

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
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = os.path.join(STATIC_URL,'admin/')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.    
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
    #'django.contrib.aderit.generic_utils.langMiddleware.SessionBasedLocaleMiddleware',
    #'django.contrib.aderit.generic_utils.currentUserMiddleware.LocalUserMiddleware',
    #'django.contrib.aderit.generic_utils.mobileMiddleware.MobileDetectionMiddleware',
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
    #'django.contrib.aderit.send_mail',
    #'captcha',
    #'django.contrib.aderit.access_account',
    #'account',
)

# Some frequent used settings
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#SESSION_COOKIE_AGE = 3600
#SESSION_SAVE_EVERY_REQUEST = True
#LOGIN_URL = "/access"
#LOGIN_REDIRECT_URL
#ACCESS_ACCOUNT_USE_CAPTCHA = False

#AUTH_PROFILE_MODULE = 'account.Account'

#DAJAXICE_MEDIA_PREFIX="dajaxice"

#CAPTCHA_FONT_SIZE = 50

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    #'filters': {
    #    'require_debug_false': {
    #        '()': 'django.utils.log.RequireDebugFalse'
    #    }
    #},
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            #'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {'class': 'logging.StreamHandler'},
        'syslog': {'class': 'logging.handlers.SysLogHandler'},


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
        'django.debug':{'handlers': ['console', 'syslog'], 'level':'DEBUG', 'propagate':True},
    }
}

### adaptable settings to override or add
from django.utils.importlib import import_module
project_settings_module_name = "%s.%s_settings" % (PROJECT_NAME, PROJECT_NAME.lower())
try:
    import_module(project_settings_module_name)
    project_settings_module = sys.modules[project_settings_module_name]
    for varname in getattr(project_settings_module, '__all__', []):
        if varname.startswith('ADDITIONAL_') and dict.has_key(locals(), varname.split('ADDITIONAL_')[1]):
            if isinstance(locals()[varname.split('ADDITIONAL_')[1]], dict):
                dict.update(locals()[varname.split('ADDITIONAL_')[1]], getattr(project_settings_module, varname))
            if isinstance(locals()[varname.split('ADDITIONAL_')[1]], (list,tuple)):
                locals()[varname.split('ADDITIONAL_')[1]] += getattr(project_settings_module, varname)
        else:
            locals()[varname] = getattr(project_settings_module, varname)
except ImportError:
    pass
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

