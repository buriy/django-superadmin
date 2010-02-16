#source: http://www.djangosnippets.org/snippets/1697/

# INSTALL NOTES:
# Register the action in your apps admin.py:
# 
# from beautils.actions import export_as_csv
# class MyAdmin(admin.ModelAdmin):
#     actions = [export_as_csv]
#     
import csv, datetime
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

def export_as_csv(modeladmin, request, queryset):
    """
    Generic csv export admin action.
    """
    if not request.user.is_staff:
        raise PermissionDenied
    opts = modeladmin.model._meta
    now = datetime.datetime.utcnow()
    time = "-".join("%02d" % x for x in now.utctimetuple()[:6])
    filename = unicode(opts).replace('.', '_') + time
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % filename
    writer = csv.writer(response)
    field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response
export_as_csv.short_description = "Export selected objects as csv file"

