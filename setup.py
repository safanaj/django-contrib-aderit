from distutils.core import setup

setup(name='DjangoContribAderit',
	version='1.3',
	description='Collection of Aderit tools for Django',
	author='Matteo Atti',
	author_email='matteo.atti@aderit.it',
	packages=['django.contrib.aderit',
		  'django.contrib.aderit.send_mail',
		  'django.contrib.aderit.access_account',
		  'django.contrib.aderit.access_account.templates',
		  'django.contrib.aderit.generic_utils',
		  'django.contrib.aderit.generic_utils.templatetags',
		  'django.contrib.aderit.generic_utils.templates'],
	requires=['Django (>=1.3)']
)
