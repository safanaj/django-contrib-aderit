from distutils.core import setup
from distutils.sysconfig import get_python_lib
import os

PKGS = ['django.contrib.aderit',
        'django.contrib.aderit.send_mail',
        'django.contrib.aderit.access_account',
        'django.contrib.aderit.generic_utils',
        'django.contrib.aderit.generic_utils.templatetags']

def get_data_files():
    _data_files_ = []
    for p in PKGS:
        founds = []
        dirp = p.replace('.','/')
        founds = os.popen2("find %s -type f -name '*.html'" % dirp)[1].read().split()
        if len(founds) > 0:
            #_data_files_.append((os.path.join(get_python_lib(), dirp, 'templates', os.path.basename(dirp)), founds))
            _data_files_.append((os.path.join(get_python_lib(), os.path.dirname(founds[0])), founds))
    return _data_files_

setup(name='DjangoContribAderit',
      version='1.3',
      description='Collection of Aderit tools for Django',
      author='Matteo Atti',
      author_email='matteo.atti@aderit.it',
      packages=PKGS,
      data_files=get_data_files(),
      requires=['Django (>=1.3)']
)
