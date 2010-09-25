# -*- coding: utf-8 -*-

""" Tablib - formats
"""

import tablib.formats._csv as csv
import tablib.formats._json as json
import tablib.formats._xls as xls
import tablib.formats._yaml as yaml

FORMATS = (csv, json, xls, yaml)
