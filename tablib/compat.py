# -*- coding: utf-8 -*-

"""
tablib.compat
~~~~~~~~~~~~~

Tablib compatiblity module.

"""

import sys

is_py3 = (sys.version_info[0] > 2)


if is_py3:
    from io import StringIO
    from statistics import median
    from itertools import zip_longest as izip_longest
    import csv
    import tablib.packages.dbfpy3 as dbfpy

    unicode = str
    xrange = range

else:
    from StringIO import StringIO
    from tablib.packages.statistics import median
    from itertools import izip_longest
    from backports import csv
    import tablib.packages.dbfpy as dbfpy

    unicode = unicode
    xrange = xrange

from MarkupPy import markup  # Kept temporarily to avoid breaking existing imports
