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
    import tablib.packages.xlwt3 as xlwt
    from tablib.packages import markup3 as markup
    from tablib.packages import openpyxl3 as openpyxl

    # py3 mappings
    ifilter = filter
    xrange = range
    unicode = str
    bytes = bytes
    basestring = str

else:
    from cStringIO import StringIO as BytesIO
    import tablib.packages.xlwt as xlwt
    from tablib.packages import markup
    from itertools import ifilter
    from tablib.packages import openpyxl

    # py2 mappings
    xrange = xrange
    unicode = unicode
    bytes = str
    basestring = basestring


