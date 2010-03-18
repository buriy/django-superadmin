from django.conf import settings
from django.contrib.admin import site
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.options import TabularInline
from django.contrib.admin.util import quote
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.importlib import import_module # django 1.2 feature
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode

def patch_admin_auth():
    import patches.auth #@UnusedImport

def patch_autosuperuser():
    import patches.syncdb #@UnusedImport

def patch_editrelated():
    import patches.editrelated #@UnusedImport

def patch_everything():
    from patches import auth, syncdb, editrelated

def get_admin_object_url(instance):
    """
    Returns the admin URL to edit the object represented by this log entry.
    This is relative to the Django admin index page.
    """
    opts = instance.__class__._meta
    root = reverse(site.root, args=[''])
    return mark_safe(u"%s%s/%s/%s/" % (root, opts.app_label, opts.object_name.lower(), quote(instance.pk)))

def get_admin_class_url(model):
    """
    Returns the admin URL to edit the object represented by this log entry.
    This is relative to the Django admin index page.
    """
    opts = model._meta
    root = reverse(site.root, args=[''])
    return mark_safe(u"%s%s/%s/" % (root, opts.app_label, opts.object_name.lower()))

def fields_to_display(model, exclude=None, func=lambda x:True):
    if exclude is None:
        exclude = [model._meta.pk.attname]
    return [x.name for x in model._meta.fields if not x.name in exclude and func(x)]

def fields_for_edit(model, exclude=None):
    return fields_to_display(model, exclude, lambda f: f.editable)

def get_unicode(self):
    try:
        name = force_unicode(self.name)[:50]
        return '[%s] %s' % (self.pk, self.name)
    except:
        return '[%s]' % self.pk
    
def shortener(name, length=50):
    name = force_unicode(name)[:length]
    if len(name) > length-3:
        return name[:length-3]+'...'
    return name

def reg_simple(model, klass=ModelAdmin, exclude=None, include=[], list_display=None, shorten=[], site=site, **options):
    if exclude is None:
        exclude = [model._meta.pk.attname]
    if list_display is None:
        list_display = fields_to_display(model, exclude) + include
    else:
        list_display = [x for x in list_display if not x in exclude] + include
    for pos, name in enumerate(list_display):
        if name in shorten:
            def shorten_wrapper(self):
                return shortener(getattr(self, name))
            shorten_wrapper.admin_order_field = name
            shorten_wrapper.short_description = name
            list_display[pos] = shorten_wrapper 
    site.register(model, klass, list_display=list_display, **options)

def reg_editable(model, list_display=None, list_editable=None, exclude=None, **options):
    if list_display is None:
        list_display = fields_to_display(model, exclude)
    if list_editable is None:
        list_editable = fields_for_edit(model, exclude)
    pk_name = model._meta.pk.attname
    if not pk_name in list_display:
        if not hasattr(model, '__unicode__'):
            model.__unicode__ = get_unicode
        list_display = ['__unicode__'] + fields_to_display(model)
    if pk_name in list_editable:
        list_editable.remove(pk_name)
    reg_simple(model, list_display=list_display, list_editable=list_editable, exclude=exclude, **options)

def reg_inline(parent, model, klass=TabularInline, exclude=[], include=[], **options):
    if parent.__module__ != model.__module__:
        try:
            import re
            path = re.sub('\.models$', '', parent.__module__)
            import_module(path+'.admin')
        except:
            import sys
            raise# ImportError("Can't import parent admin"), None, sys.exc_info()[2]
    
    parent_admin = site._registry[parent]
    options['__module__'] = __name__
    options['model'] = model
    options['fields'] = include or fields_to_display(model)
    options['exclude'] = exclude
    inline = type("%sInline" % model.__name__, (klass,), options)

    if not parent_admin.inlines:
        parent_admin.inlines = []
    parent_admin.inlines.append(inline)
    if not parent_admin.inline_instances:
        parent_admin.inline_instances = []
    parent_admin.inline_instances.append(inline(parent, site))

def reg_all(module, excludes=[], **opts):
    from django.db.models.base import ModelBase, Model
    for name in dir(module):
        if name in excludes: continue
        model = getattr(module, name)
        if model in excludes: continue
        if type(model) is ModelBase and issubclass(model, Model) and hasattr(model, '_meta'):
            reg_editable(model, **opts)