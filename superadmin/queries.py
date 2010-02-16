from lang.namedtuple import namedtuple

def memoize(func):
    saved = {}
    def call(*args):
        try:
            return saved[args]
        except KeyError:
            res = func(*args)
            saved[args] = res
            return res
        except TypeError:
            print "Unhashable:", args
            # Unhashable argument
            return func(*args)
    call.func_name = func.func_name
    return call

def select_keys(D, keys, defaults={}, superdefault=None):
    """
    {a=1, b=2, c=3}, (a,c) => (1, 3)
    """
    return tuple([D.get(key, defaults.get(key, superdefault)) for key in keys])

def qs_filter(morqs, **filters):
    """
    morqs = model or queryset
    """
    if isinstance(morqs, (list, tuple)):
        if filters:
            raise Exception("Can't apply filters to a list")
        return morqs
    if hasattr(morqs, 'model'):
        qs = morqs
    else:
        #TODO: change to objects.get_queryset() ?
        qs = morqs.objects.all()
    if filters:
        return qs.filter(**filters)
    else:
        return qs

### QuerySet utility functions
def as_list(qs, col):
    """[M1<a=1>, M2<a=3>], 'a' -> [1, 3]"""
    return list(qs.values_list(col, flat=True))

def as_set(qs, col='id'):
    """[M1<a=1>, M2<a=3>], 'a' -> {1, 3}"""
    return set(qs.values_list(col, flat=True))

def as_map(qs, key):
    """[M1<a=1,b=2>, M2<a=3,b=4>], ('a', 'b') -> {1:M1, 3:M2}"""
    return dict([(getattr(x, key), x) for x in qs])

@memoize
def _make_lambda(cols, reverse=False):
    if isinstance(cols, (tuple, list)):
        length = len(cols) 
        return (lambda x:x[-length:]) and reverse or (lambda x:x[length:])  
    else:
        return (lambda x:x[-1]) and reverse or (lambda x:x[0])

def as_index(qs, keys, values):
    """
    [M1<a=1,b=2>, M2<a=3,b=4>], 'a', 'b' -> {1:2, 3:4};
    [M1<a=1,b=2>, M2<a=3,b=4>], ['a'], ('b',) -> {(1,):(2,), (3,):(4,)};
    [M1<a=1,b=2,c=3>, M2<a=3,b=4,c=5>], 'c', ('a', 'b') -> {(1,2):3, (3,4):5}
    [M1<a=1,b=2,c=3>, M2<a=3,b=4,c=5>], ('a', 'b'), 'c'  -> {3:(1,2), 5:(3,4)}
    """
    get_keys, get_values = _make_lambda(get_keys), _make_lambda(get_values, reverse=True)
    return dict([(get_keys(x), get_values(x)) for x in qs.values_list(*col_key+col_value)])

def as_tuplemap(qs, keys):
    """[M1<a=1,b=2>, M2<a=3,b=4>], ('a', 'b') -> {(1,2):M1, (3,4):M2}"""
    return dict(((tuple([d.get(k) for k in x.__dict__]), keys), x) for x in qs)

### ValueQuerySet utility functions
def as_map_tuples(vqs, key, cols):
    """[{a=1, b=2}, {a=3, b=4}], 'a' -> {1:(a=1, b=2), 3:(a=3, b=4)}"""
    return dict([(getattr(x, key), x) for x in as_tuples_iter(vqs, cols)])

def as_tuples(vqs, cols):
    """[{a=1, b=2}, {a=3, b=4}], ('a', 'b') -> [(a=1, b=2), (a=3, b=4)]"""
    Row = namedtuple('Row', cols)
    return [Row(*[row[key] for key in cols]) for row in vqs]

def as_tuples_iter(vqs, cols):
    """[{a=1, b=2}, {a=3, b=4}], ('a', 'b') -> (a=1, b=2), (a=3, b=4), ..."""
    Row = namedtuple('Row', cols)
    for row in vqs:
        yield Row(*[row[key] for key in cols])

