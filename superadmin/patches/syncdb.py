#http://www.djangosnippets.org/snippets/1875/
#renamed "test" to "admin" since the last makes more sense
#!/usr/bin/env python

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth.management import create_superuser
from django.db.models import signals
from django.contrib.auth.models import User

# From http://stackoverflow.com/questions/1466827/ --
#
# Prevent interactive question about wanting a superuser created.    (This code
# has to go in this otherwise empty "models" module so that it gets processed by
# the "syncdb" command during database creation.)
signals.post_syncdb.disconnect(
        create_superuser,
        sender=auth_models,
        dispatch_uid='django.contrib.auth.management.create_superuser')

# Create our own admin user automatically.

def create_adminuser(app, created_models, verbosity, **kwargs):
    if not settings.DEBUG:
        return
    try:
        User.objects.get(username='admin')
    except User.DoesNotExist:
        print '*' * 80
        print 'Creating administrator account (login: admin, password: admin)'
        print '*' * 80
        assert User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
    else:
        print 'Administrator account already exists.'

signals.post_syncdb.connect(create_adminuser,
        sender=auth_models, dispatch_uid='common.models.create_adminuser')
