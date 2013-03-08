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
    import tablib.packages.xlrd as xlrd
    from tablib.packages.xlrd3.biffh import XLRDError
    from tablib.packages import markup3 as markup
    from tablib.packages import openpyxl3 as openpyxl
    from tablib.packages.odf3 import opendocument, style, text, table

    import csv
    from io import StringIO
    # py3 mappings

    unicode = str
    bytes = bytes
    basestring = str

else:
    from cStringIO import StringIO as BytesIO
    from cStringIO import StringIO
    import tablib.packages.xlwt as xlwt
    import tablib.packages.xlrd as xlrd
    from tablib.packages.xlrd.biffh import XLRDError
    from tablib.packages import markup
    from itertools import ifilter
    from tablib.packages import openpyxl
    from tablib.packages.odf import opendocument, style, text, table

    from tablib.packages import unicodecsv as csv

    unicode = unicode
