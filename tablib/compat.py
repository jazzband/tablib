# -*- coding: utf-8 -*-

"""
tablib.compat
~~~~~~~~~~~~~

Tablib compatiblity module.

"""

import sys

is_py3 = (sys.version_info[0] > 2)



try:
    from collections import OrderedDict
except ImportError:
    from tablib.packages.ordereddict import OrderedDict


if is_py3:
    from io import BytesIO
    from tablib.packages import markup3 as markup
    import tablib.packages.dbfpy3 as dbfpy

    import csv
    from io import StringIO
    # py3 mappings

    ifilter = filter
    unicode = str
    bytes = bytes
    basestring = str
    xrange = range

else:
    from cStringIO import StringIO as BytesIO
    from cStringIO import StringIO
    from tablib.packages import markup
    from itertools import ifilter

    import unicodecsv as csv
    import tablib.packages.dbfpy as dbfpy

    unicode = unicode
    xrange = xrange
