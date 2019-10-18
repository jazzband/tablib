""" Tablib - DataFrame Support.
"""

import sys
from io import BytesIO

try:
    from pandas import DataFrame
except ImportError:
    DataFrame = None

import tablib

from tablib.compat import unicode

title = 'df'
extensions = ('df', )

def detect(stream):
    """Returns True if given stream is a DataFrame."""
    if DataFrame is None:
        return False
    try:
        DataFrame(stream)
        return True
    except ValueError:
        return False


def export_set(dset, index=None):
    """Returns DataFrame representation of DataBook."""
    if DataFrame is None:
        raise NotImplementedError(
            'DataFrame Format requires `pandas` to be installed.'
            ' Try `pip install tablib[pandas]`.')
    dataframe = DataFrame(dset.dict, columns=dset.headers)
    return dataframe


def import_set(dset, in_stream):
    """Returns dataset from DataFrame."""
    dset.wipe()
    dset.dict = in_stream.to_dict(orient='records')
