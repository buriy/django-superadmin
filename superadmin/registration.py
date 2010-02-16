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
import admin_auth #@UnusedImport

def render_add_link(site, opts, name):
    info = (opts.app_label, opts.object_name.lower())
    try:
        related_url = reverse('admin:%s_%s_add' % info, current_app=site.name)
    except NoReverseMatch:
        info = (site.root_path, opts.app_label, opts.object_name.lower())
        related_url = '%s%s/%s/add/' % info
    # TODO: "id_" is hard-coded here. This should instead use the correct
    # API to determine the ID dynamically.
    output = []
    output.append(u'<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
        (related_url, name))
    output.append(u'<img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Add Another')))
    return output

def render_edit_link(site, opts, name, value):
    info = (opts.app_label, opts.object_name.lower())
    try:
        related_url = reverse('admin:%s_%s_change' % info, args=(value,), current_app=site.name)
    except NoReverseMatch:
        info = (site.root_path, opts.app_label, opts.object_name.lower(), value)
        related_url = '%s%s/%s/%s/' % info
    # TODO: "id_" is hard-coded here. This should instead use the correct
    # API to determine the ID dynamically.
    output = []
    output.append(u'<a href="%s" class="edit-it" id="edit_id_%s"> ' % \
        (related_url, name))
    output.append(u'<img src="%simg/admin/icon_changelink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Edit object')))
    return output

def new_render(self, name, value, *args, **kwargs):
    rel_to = self.rel.to
    self.widget.choices = self.choices
    output = [self.widget.render(name, value, *args, **kwargs)]

    if rel_to in self.admin_site._registry: # If the related object has an admin interface:
        output.extend(render_add_link(self.admin_site, rel_to._meta, name))
        if value and not isinstance(value, list):
            output.extend(render_edit_link(self.admin_site, rel_to._meta, name, value))
    
    return mark_safe(u''.join(output))

original_render = RelatedFieldWidgetWrapper.render
RelatedFieldWidgetWrapper.render = new_render

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
    
def shortener(name):
    name = force_unicode(name)[:50]
    if len(name)>47: return name[:47]+'...'
    return name

def reg_simple(model, klass=ModelAdmin, exclude=None, include=[], list_display=None, shorten=[], site=site, **options):
    if exclude is None:
        exclude = [model._meta.pk.attname]
    if list_display is None:
        list_display = fields_to_display(model, exclude) + include
    else:
        list_display = [x for x in list_display if not x in exclude] + include
    short = lambda x: lambda self: shortener(getattr(self, x))
    list_display = [(x in shorten) and short(x) or x for x in list_display]
    print list_display
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