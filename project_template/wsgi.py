# pylint: disable-msg=C0111,C0103
import os
import sys

project_path = os.path.abspath(os.path.dirname(__file__))
project_name = os.path.basename(project_path)

path = os.path.abspath(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.append(path)

path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if path not in sys.path:
    sys.path.append(path)

custom_settings_filename = "%s_settings.py" % project_name.lower()
if os.path.exists(os.path.join(project_path, custom_settings_filename)):
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s_settings' % project_name.lower()
else:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
