""" Tablib - DataFrame Support.
"""


import sys


if sys.version_info[0] > 2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from pandas import DataFrame

import tablib

from tablib.compat import unicode

title = 'df'
extensions = ('df', )

def detect(stream):
    """Returns True if given stream is a DataFrame."""
    try:
        DataFrame(stream)
        return True
    except ValueError:
        return False


def export_set(dset, index=None):
    """Returns DataFrame representation of DataBook."""
    dataframe = DataFrame(dset.dict, columns=dset.headers)
    return dataframe


def import_set(dset, in_stream):
    """Returns dataset from DataFrame."""
    dset.wipe()
    dset.dict = in_stream.to_dict(orient='records')
