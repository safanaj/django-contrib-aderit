from distutils.core import setup

setup(name='DjangoContribAderit',
      version='1.3',
      description='Collection of Aderit tools for Django',
      author='Matteo Atti',
      author_email='matteo.atti@aderit.it',
      packages=['django.contrib.aderit',
                'django.contrib.aderit.send_mail',
                'django.contrib.aderit.access_account',
                'django.contrib.aderit.generic_utils',
                'django.contrib.aderit.generic_utils.templatetags'],
      # package_data={'django.contrib.aderit.access_account':['templates/*.html'],
      #               'django.contrib.aderit.generic_utils':['templates/*.html'],
      #               },
      data_files=[
        ('share/pyshared/django/contrib/aderit/generic_utils/templates',
         ['django/contrib/aderit/generic_utils/templates/tags/last_logins.html',
          'django/contrib/aderit/generic_utils/templates/tags/online_users.html',
          'django/contrib/aderit/generic_utils/templates/tags/last_registers.html']),
        ('share/pyshared/django/contrib/aderit/access_account/templates',
         ['django/contrib/aderit/access_account/templates/access_account/chprofile.html',
          'django/contrib/aderit/access_account/templates/access_account/post_creation.html',
          'django/contrib/aderit/access_account/templates/access_account/profile.html',
          'django/contrib/aderit/access_account/templates/access_account/forgotpsw.html',
          'django/contrib/aderit/access_account/templates/access_account/chpsw.html',
          'django/contrib/aderit/access_account/templates/access_account/forgotpswreset.html',
          'django/contrib/aderit/access_account/templates/access_account/access_accountcontrol.html'
          ])
        ],
      requires=['Django (>=1.3)']
)
