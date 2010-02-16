#Example; Named tuple benchmark.

#Do imports.
from namedtuple import namedtuple
from timeit import Timer

"""
This module allows one to use tuples similarly to structs -- you can access 
each index by a named attribute as well. This is similar to 
collections.namedtuple in Python 2.6 or the recipe at
http://code.activestate.com/recipes/500261/ but does not do any code string
generation or eval manipulation. Usable in Python 2.4+.

>>> import namedtuples
>>> tpl = namedtuples.namedtuple(['a', 'b', 'c'])
>>> tpl(1, 2, 3)
(1, 2, 3)
>>> tpl(1, 2, 3).b
2
>>> tpl(c=1, a=2, b=3)
(2, 3, 1)
>>> tpl(c=1, a=2, b=3).b
3
>>> tpl(c='pads with nones')
(None, None, 'pads with nones')
>>> tpl(b='pads with nones')
(None, 'pads with nones', None)
>>> 
"""

from operator import itemgetter

_known_tuple_types = {}

class NamedTupleBase(tuple):
    """Base class for named tuples with the __new__ operator set, named tuples
       yielded by the namedtuple() function will subclass this and add
       properties."""
    def __new__(cls, *args, **kws):
        """Create a new instance of this fielded tuple"""
        # May need to unpack named field values here
        if kws:
            values = list(args) + [None]*(len(cls._fields) - len(args))
            fields = dict((val, idx) for idx, val in enumerate(cls._fields))
            for kw, val in kws.iteritems():
                assert kw in kws, "%r not in field list" % kw
                values[fields[kw]] = val
            args = tuple(values)
        return tuple.__new__(cls, args)

def namedtuple2(fieldnames):
    """Create a subclass of Python's built-in """
    # Split up a string, some people do this
    if isinstance(fieldnames, basestring):
        fieldnames = fieldnames.replace(',', ' ').split()
    # Convert anything iterable that enumerates fields to a tuple now
    fieldname_tuple = tuple(str(field) for field in fieldnames)
    # See if we've cached this
    if fieldname_tuple in _known_tuple_types:
        return _known_tuple_types[fieldname_tuple]
    # Make the type
    new_tuple_type = type('namedtuple|%s'%','.join(fieldname_tuple), 
            (NamedTupleBase,), {})
    # Set the hidden field
    new_tuple_type._fields = fieldname_tuple
    # Add the getters
    for i, field in enumerate(fieldname_tuple):
        setattr(new_tuple_type, field, property(itemgetter(i)))
    # Cache
    _known_tuple_types[fieldname_tuple] = new_tuple_type
    # Done
    return new_tuple_type

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
            # Unhashable argument
            return func(*args)
    call.func_name = func.func_name
    return call

#Create a named tuple type along with fields.
MyTuple = namedtuple("one two three")
print MyTuple
#Instantiate a test named tuple and dictionary.
my_tuple = MyTuple(one=1, two=2, three=3)
my_dict = {"one":1, "two":2, "three":3}

#namedtuple = memoize(namedtuple)
#Test function.  Read tuple values.
k = ("one", "two", "three")
v = (1, 2, 3)

def create_nuple():
  #MyTuple=namedtuple("MyTuple", "one two three")
  MyTuple(v)

def create_nuple2():
  MyTuple=namedtuple("one two three")
  MyTuple(v)

def create_tuple():
    tuple(v)

def create_dict():
    {"one":1, "two":2, "three":3}

def create_dict2():
    dict(zip(k, v))

def empty():
    pass

#Test function.  Read tuple values.
def run_nuple():
  one = my_tuple.one
  two = my_tuple.two
  three = my_tuple.three

#Test function.  Read tuple values.
def run_tuple():
  one = my_tuple[0]
  two = my_tuple[1]
  three = my_tuple[2]

#Test function.  Read dictionary values.
def run_dict():
  one = my_dict["one"]
  two = my_dict["two"]
  three = my_dict["three"]

def test(f, c=1000000):
    n = f.func_name
    print "%30s:" % n,
    r = Timer("%s()" % n, "from __main__ import " + n).timeit(c)
    print int(r * 1000), 'ms => ', int(c / r), 'times per second'

#Main.
if __name__ == "__main__":

  for t in [empty, create_tuple, create_dict, create_nuple, create_dict2, create_nuple2]:
      test(t)
    
  
#  print "MAKE TUPLE: ", Timer("run_tuple()", "from __main__ import run_tuple").timeit(1000000)
