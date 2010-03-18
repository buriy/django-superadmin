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
