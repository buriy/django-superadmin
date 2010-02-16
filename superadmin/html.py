from django.conf import settings
from django.utils.safestring import mark_safe

def link(url, text='', classes=''):
    if not text: text = url
    if classes: classes = ' class="%s"' % classes
    return mark_safe("""<a href="%s"%s>%s</a>""" % (url, classes, text))

def img(url, alt='', classes=''):
    if not url.startswith('http://') and not url[:1]=='/':
        #add media url to relative paths
        url = settings.MEDIA_URL + url
    if classes: classes = ' class="%s"' % classes
    if alt: alt = ' alt="%s" title="%s"' % (alt, alt)
    return mark_safe("""<img src="%s"%s%s>""" % (url, classes, alt))

def get_admin_url(self):
    #...

def admin_edit_link(instance):
    from utils.admin import get_admin_object_url
    return link(get_admin_object_url(instance), unicode(instance))

def admin_add_link(model, params=''):
    from utils.admin import get_admin_class_url
    return link(get_admin_class_url(model)+'add/'+params, '&nbsp;', 'addlink')

def admin_link(model, text, classes='', extra_path=''):
    from utils.admin import get_admin_class_url
    return link(get_admin_class_url(model)+extra_path, text, classes)

def admin_view_children(queryset, childtype, ref):
    links = [
        admin_add_link(childtype, ref),
        admin_link(childtype, unicode(queryset.count()), extra_path=ref)
    ]
    return ' '.join(links)

