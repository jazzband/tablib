# -*- coding: utf-8 -*-

""" Tablib - formats
"""

from . import _csv as csv
from . import _json as json
from . import _xls as xls
from . import _yaml as yaml
from . import _tsv as tsv
from . import _html as html
from . import _xlsx as xlsx
from . import _ods as ods
from . import _dbf as dbf
from . import _latex as latex
from . import _df as df
from . import _rst as rst
from . import _jira as jira

# xlsx before as xls (xlrd) can also read xlsx
available = (json, xlsx, xls, yaml, csv, dbf, tsv, html, jira, latex, ods, df, rst)
