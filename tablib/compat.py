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

else:
    from cStringIO import StringIO as BytesIO
    import tablib.packages.xlwt as xlwt
    from tablib.packages import markup


