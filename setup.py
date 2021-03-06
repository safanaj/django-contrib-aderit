from distutils.core import setup
from distutils.sysconfig import get_python_lib
import os

### cmdclasses = {'install_data': install_data} ### what is this ?
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
django_contrib_aderit_root_dir = 'django'


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

for dirpath, dirnames, filenames in os.walk(django_contrib_aderit_root_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([os.path.join(get_python_lib(), dirpath),
                           [os.path.join(dirpath, f) for f in filenames]])

project_template_prefix = 'share/python-django-contrib-aderit'
for dirpath, dirnames, filenames in os.walk('project_template'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if filenames:
        data_files.append([os.path.join(project_template_prefix, dirpath),
                           [os.path.join(dirpath, f) for f in filenames]])

setup(name='DjangoContribAderit',
      version='1.4.6.6',
      description='Collection of Aderit tools for Django',
      author='Matteo Atti',
      author_email='matteo.atti@aderit.it',
      packages=packages,
      data_files=data_files,
      scripts=['django-admin-aderit'],
      requires=['Django (>=1.3)']
)
