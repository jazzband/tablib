# -*- coding: utf-8 -*-
import csv
from csv import *

#http://semver.org/
VERSION = (0, 8, 0)
__version__ = ".".join(map(str,VERSION))

def _stringify(s, encoding):
    if type(s)==unicode:
        return s.encode(encoding)
    elif isinstance(s, (int , float)):
        pass #let csv.QUOTE_NONNUMERIC do its thing.
    elif type(s) != str:
        s=str(s)
    return s

def _stringify_list(l, encoding):
    return [_stringify(s, encoding) for s in l]

class UnicodeWriter(object):
    """
    >>> import unicodecsv
    >>> from cStringIO import StringIO
    >>> f = StringIO()
    >>> w = unicodecsv.writer(f, encoding='utf-8')
    >>> w.writerow((u'é', u'ñ'))
    >>> f.seek(0)
    >>> r = unicodecsv.reader(f, encoding='utf-8')
    >>> row = r.next()
    >>> print row[0], row[1]
    é ñ
    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.writer = csv.writer(f)
        self.dialect = dialect
        self.encoding = encoding
        self.writer = csv.writer(f, dialect=dialect, **kwds)

    def writerow(self, row):
        self.writer.writerow(_stringify_list(row, self.encoding))

    def writerows(self, rows):
        for row in rows:
          self.writerow(row)
writer = UnicodeWriter

class UnicodeReader(object):
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.encoding = encoding

    def next(self):
        row = self.reader.next()
        return [unicode(s, self.encoding) for s in row]

    def __iter__(self):
        return self
reader = UnicodeReader

class DictWriter(csv.DictWriter):
    """
    >>> from cStringIO import StringIO
    >>> f = StringIO()
    >>> w = DictWriter(f, ['a', 'b'], restval=u'î')
    >>> w.writerow({'a':'1'})
    >>> w.writerow({'a':'1', 'b':u'ø'})
    >>> w.writerow({'a':u'é'})
    >>> f.seek(0)
    >>> r = DictReader(f, fieldnames=['a'], restkey='r')
    >>> r.next() == {'a':u'1', 'r':[u"î"]}
    True
    >>> r.next() == {'a':u'1', 'r':[u"ø"]}
    True
    >>> r.next() == {'a':u'é', 'r':[u"î"]}
    """
    def __init__(self, csvfile, fieldnames, restval='', extrasaction='raise', dialect='excel', encoding='utf-8', *args, **kwds):
        self.fieldnames = fieldnames
        self.encoding = encoding
        self.restval = restval
        self.writer = csv.DictWriter(csvfile, fieldnames, restval, extrasaction, dialect, *args, **kwds)
    def writerow(self, d):
        for fieldname in self.fieldnames:
            if fieldname in d:
                d[fieldname] = _stringify(d[fieldname], self.encoding)
            else:
                d[fieldname] = _stringify(self.restval, self.encoding)
        self.writer.writerow(d)

class DictReader(csv.DictReader):
    def __init__(self, csvfile, fieldnames=None, restkey=None, restval=None, dialect='excel', encoding='utf-8', *args, **kwds):
        self.restkey = restkey
        self.encoding = encoding
        self.reader = csv.DictReader(csvfile, fieldnames, restkey, restval, dialect, *args, **kwds)
    def next(self):
        d = self.reader.next()
        for k, v in d.items():
            if k == self.restkey:
                rest = v
                if rest:
                    d[self.restkey] = [unicode(v, self.encoding) for v in rest]
            else:
                if v is not None:
                    d[k] = unicode(v, self.encoding)
        return d
