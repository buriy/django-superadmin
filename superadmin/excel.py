from queries import qs_filter
import csv

def seq_uniq(S):
    r = []
    for item in S:
        if not item in r:
            r.append(item)
    return r

class SkipLine: pass
class SkipFile: pass

DATE_FORMATS = ['%d-%b-%y', '%m/%d/%y', '%m/%d/%Y', '%d %B %Y']

def parse_excel_date(d, formats = DATE_FORMATS):
    import datetime
    import time
    d = d.strip()
    exception = None
    for format in formats:
        try:
            #return datetime.datetime.strptime(d, format).date()
            return datetime.date(*(time.strptime(d, format)[0:3]))
        except ValueError, e:
            exception = e
    if exception:
        #show only exception about last format parse failed
        raise exception

def format_excel_date(d):
    return d.strptime('%Y-%m-%d') # ISO

def parse_string(s):
    try:
        return s.decode('utf-8')
    except UnicodeDecodeError:
        return s.decode('latin1')

def parse_number(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def force_quote(s):
    if '"' in s: # escape all '"' into '\"'
        s = s.replace('"', '\\"')
    return '"%s"' % s

def quote(s, chars = ' ,"'):
    for c in chars:
        if c in s:
            return force_quote(s)
    return s

def export_csv(stream, morqs, strings, dates={}, overrides={}):
    w = csv.writer(stream)
    qs = qs_filter(morqs)
    field_names = seq_uniq(strings.keys() + dates.keys() + overrides.keys())
    w.write(map(force_quote, field_names))
    for row in qs:
        try:
            d = {}
            for k,v in strings.items():
                item = row[k].unicode(v).encode('utf-8')
                d[k] = quote(item)
            for k,v in dates.items():
                d[k] = format_excel_date(row[k])
            for k, func in overrides.items():
                value = func
                if callable(func):
                    value = func(d, row[k])
                d[k] = value
            w.write([d[k] for k in field_names])
        except SkipLine:
            continue
        except SkipFile:
            break
    return w

def sample_usage():
    strings = {
        'Contact details': 'contact',
        'Description': 'description',
        'Event Name': 'name',
        'Event Type': 'event_type',
        'Event Organiser': 'organizer',
        'Link URL': 'link_url',
        'Location': 'location',
        'Notes': 'notes'
    }
    
    dates = {
        'End Date': 'end_date',
        'Start Date': 'start_date',
    }
    
    from apps.places.models import Event #@UnresolvedImport
    
    #fn = 'Offshore Events_WN_CSV.csv'
    #items = import_csv(fn, Event, 'name', strings, dates, save=False)
    #print "Imported %s items." % len(items)
    export_csv(open('Offshort Events New.csv', 'w'), Event, strings, dates)

if __name__ == '__main__':
    sample_usage()