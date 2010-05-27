from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin.util import quote

def admin_url_for_object(site, instance):
    """
    Returns the admin URL to edit the object represented by this log entry.
    This is relative to the Django admin index page.
    """
    opts = instance.__class__._meta
    root = reverse(site.root, args=[''])
    return mark_safe(u"%s%s/%s/%s/" % (root, opts.app_label, opts.object_name.lower(), quote(instance.pk)))

def admin_url_for_class(site, model):
    """
    Returns the admin URL to edit the object represented by this log entry.
    This is relative to the Django admin index page.
    """
    opts = model._meta
    root = reverse(site.root, args=[''])
    return mark_safe(u"%s%s/%s/" % (root, opts.app_label, opts.object_name.lower()))
