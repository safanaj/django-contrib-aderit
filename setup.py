from distutils.core import setup

setup(name='ContribAderit',
	version='1.0',
	description='Collection of Aderit tools for Django',
	author='Matteo Atti',
	author_email='matteo.atti@aderit.it',
	packages=['django.contrib.aderit.send_mail','django.contrib.aderit.generic_utils','django.contrib.aderit.generic_utils.templatetags','django.contrib.aderit.generic_utils.templates'],
	requires=['Django (>=1.3)']
)
