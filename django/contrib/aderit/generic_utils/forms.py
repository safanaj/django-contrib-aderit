__doc__ = "Generic forms and form factory utils"
from types import ClassType
from django.db import models as django_models
from django.forms.models import modelform_factory, modelformset_factory, BaseModelForm
from django.forms.formsets import formset_factory
from django.forms.forms import BaseForm, Form
from django.utils.datastructures import SortedDict

def generic_formclass_factory(classes, bases=[], prepend_fields=False,
                              fields_uniqueness=True, uniqueness_prefix='',
                              sorted_fields=SortedDict()):
    """
    General form factory, inspired from 'django.forms.models.modelform_factory'.

    @classes should be a list of: Model or ModelForm or Form based classes.
    @sorted_fields values should be 'django.forms.fields.Field' based class.
       es: generic_formclass_factory(..., prepend_fields=True,
                                     sorted_fields=SortedDict({
                                        'mail_address' : django.forms.fields.CharField(),
                                        'age' : django.forms.fields.IntegerField(min_value=0),
                                        'birthday' : django.forms.fields.DateField() }))
           generate a Form class based which base_fields are:
           {
           'mail_address' : <CharField object>, 'age': <positive IntegerField object>,
           'birthday': <DateField object>,
           ... other forms fields from classes ...
           }
           to produce:
           <input type="text" name='mail_address' value="... some initial value..." /> etc ...

    @prepend_fields: if True, keywords fields are prepended insted appended.
    @fields_uniqueness and @uniqueness_prefix to avoid several base_fields override other base_fields

    TODO: add keywords to more flexibility and to control modelform_factory (see can_delete for checkbox)
    """
    def make_fields_unique(fields, prefix=uniqueness_prefix, prepending=SortedDict(), appending=SortedDict()):
        uniq_fields = SortedDict()
        for i, kv in enumerate(prepending.items()):
            if kv[0] in fields:
                if "%s%s" % (prefix, kv[0]) in fields:
                    idx = "_%d" % i
                    uniq_fields.update({ prefix + kv[0] + idx : kv[1] })
                else:
                    uniq_fields.update({ prefix + kv[0] : kv[1] })
            else:
                uniq_fields.update({ kv[0] : kv[1] })
        uniq_fields.update(fields)
        for i, kv in enumerate(appending.items()):
            if kv[0] in fields:
                if "%s%s" % (prefix, kv[0]) in fields:
                    idx = "_%d" % i
                    uniq_fields.update({ prefix + kv[0] + idx : kv[1] })
                else:
                    uniq_fields.update({ prefix + kv[0] : kv[1] })
            else:
                uniq_fields.update({ kv[0] : kv[1] })
        return uniq_fields

    if not isinstance(classes, (list, tuple)):
        classes = [classes]
    if len(bases) < 1:
        bases.append(Form)
    new_form_class = type("GenericForm", tuple(bases), {})

    if prepend_fields:
        prepended_base_fields = sorted_fields
        if fields_uniqueness:
            prepended_base_fields = make_fields_unique(new_form_class.base_fields,
                                                       prepending=prepended_base_fields)
        else:
            prepended_base_fields.update(new_form_class.base_fields)
        new_form_class.base_fields = prepended_base_fields

    for klass in classes:
        if not isinstance(klass, (type, ClassType)): # klass is an instance
            klass = getattr(klass, '__class__', None)
        if klass is None:
            continue  # skip None class
        if issubclass(klass, django_models.Model): # use modelform_factory
            if fields_uniqueness:
                appending_fields = modelform_factory(klass).base_fields
                klass_prefix = "%s_" % klass.__name__.lower()
                uniq_fields = make_fields_unique(new_form_class.base_fields,
                                                 prefix=klass_prefix,
                                                 appending=appending_fields)
                new_form_class.base_fields.update(uniq_fields)
            else:
                new_form_class.base_fields.update(modelform_factory(klass).base_fields)
        elif issubclass(klass, (BaseModelForm, BaseForm)) and hasattr(klass, 'base_fields'):
            if fields_uniqueness:
                klass_prefix = "%s_" % klass.__name__.lower()
                uniq_fields = make_fields_unique(new_form_class.base_fields,
                                                 prefix=klass_prefix,
                                                 appending=klass.base_fields)
                new_form_class.base_fields.update(uniq_fields)
            else:
                new_form_class.base_fields.update(klass.base_fields)

    if not prepend_fields:
        if fields_uniqueness:
            uniq_fields = make_fields_unique(new_form_class.base_fields,
                                             appending=sorted_fields)
            new_form_class.base_fields.update(uniq_fields)
        else:
            new_form_class.base_fields.update(sorted_fields)

    return new_form_class

