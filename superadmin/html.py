from django.conf import settings
from django.utils.safestring import mark_safe
from superadmin.refs import admin_url_for_class, admin_url_for_object

def link(url, text=None, classes=None):
    if text is None:
        text = url
    if classes is not None:
        classes = ' class="%s"' % classes
    return mark_safe("""<a href="%s"%s>%s</a>""" % (url, classes, text))

def img(url, alt=None, classes=''):
    if not url.startswith('http://') and not url.startswith('/'):
        #add media url to relative paths
        url = settings.MEDIA_URL + url
    if classes is not None:
        classes = ' class="%s"' % classes
    if alt is not None:
        alt = ' alt="%s" title="%s"' % (alt, alt)
    return mark_safe("""<img src="%s"%s%s>""" % (url, classes, alt))

def admin_link_for_edit(site, instance):
    return link(admin_url_for_object(site, instance), unicode(instance))

def admin_link_for_add(site, model, params=''):
    return link(admin_url_for_class(site, model)+'add/'+params, '&nbsp;', 'addlink')

def admin_link_custom(site, model, text, classes='', extra_path=''):
    return link(admin_url_for_class(site, model)+extra_path, text, classes)

def admin_view_children(site, queryset, childtype, ref):
    links = [
        admin_link_for_add(site, childtype, ref),
        admin_link_custom(site, childtype, unicode(queryset.count()), extra_path=ref)
    ]
    return ' '.join(links)