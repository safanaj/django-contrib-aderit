# -*- coding: utf-8 -*-

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.conf import settings
from django.contrib.aderit.access_account.models import *
import logging, os, re

@dajaxice_register
def chprofilepop(request):
    dajax = Dajax()
    user = AccessAccount.objects.get(user=request.user)
    dajax.assign('#id_nickname','value',request.user.username)
    dajax.assign('#id_first_name','value',request.user.first_name)
    dajax.assign('#id_last_name','value',request.user.last_name)
    dajax.assign('#id_email','value',request.user.email)
    dajax.assign('#id_phone','value',user.phone)
    dajax.assign('#id_phone_mobile','value',user.mobile_phone)
    dajax.assign('#id_company','value',user.company)
    dajax.assign('#id_partita_iva','value',user.partita_iva)
    dajax.assign('#id_address','value',user.address)
    dajax.assign('#id_cap','value',user.cap)
    dajax.assign('#id_location','value',user.location)
    dajax.assign('#id_paese','value',user.paese)
    return dajax.json()

