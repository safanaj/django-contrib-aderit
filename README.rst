##########
Django Contrib Aderit
##########

Collection of Aderit tools for Django.

Django framework extensions by Aderit srl.

Modules:
 * GenericUtils (django.contrib.aderit.generic_utils): 
    - extension to django.generic.base.View to allow
      smart decoration via attibutes (GenericUtilView)
    - some useful middlewares (from several snippets)
    - generic_formclass_factory inspired from modelform_factory
    - django.db.models.fields.CharField extension to implement
      a GenericPhoneField for models, using a customizable
      GenericPhoneField for forms
    - model admin generic action to export in csv
    - some useful templatetags (from several snippets)
 * AccessAccount (django.contrib.aderit.access_account):
    abstract user profile and django.contrib.auth.views rewritten
    using Class-based views
 * SendMail (django.contrib.aderit.send_mail):
    to manage template mails via database
 * News (django.contrib.aderit.news):
    a simple app to manage news on sites

More information on `our website <http://www.aderit.it>`_.

*************
Documentation
*************

TODO

************
Getting Help
************

Please send an email to info@aderit.it, or send an email
directly to bardelli.marco@gmail.com

*******
Credits
*******

* `Django project <http://www.djangoproject.com>`

