""" Tablib - DBF Support.
"""
import io
import os
import tempfile

from tablib.packages.dbfpy import dbf
from tablib.packages.dbfpy import dbfnew
from tablib.packages.dbfpy import record as dbfrecord


title = "dbf"
extensions = ("csv",)

DEFAULT_ENCODING = "utf-8"


def export_set(dataset):
    """Returns DBF representation of a Dataset"""
    new_dbf = dbfnew.dbf_new()
    temp_file, temp_uri = tempfile.mkstemp()

    # create the appropriate fields based on the contents of the first row
    first_row = dataset[0]
    for fieldname, field_value in zip(dataset.headers, first_row):
        if type(field_value) in [int, float]:
            new_dbf.add_field(fieldname, "N", 10, 8)
        else:
            new_dbf.add_field(fieldname, "C", 80)

    new_dbf.write(temp_uri)

    dbf_file = dbf.Dbf(temp_uri, readOnly=0)
    for row in dataset:
        record = dbfrecord.DbfRecord(dbf_file)
        for fieldname, field_value in zip(dataset.headers, row):
            record[fieldname] = field_value
        record.store()

    dbf_file.close()
    dbf_stream = open(temp_uri, "rb")
    stream = io.BytesIO(dbf_stream.read())
    dbf_stream.close()
    os.close(temp_file)
    os.remove(temp_uri)
    return stream.getvalue()


def import_set(dset, in_stream, headers=True):
    """Returns a dataset from a DBF stream."""

    dset.wipe()
    _dbf = dbf.Dbf(io.BytesIO(in_stream))
    dset.headers = _dbf.fieldNames
    for record in range(_dbf.recordCount):
        row = [_dbf[record][f] for f in _dbf.fieldNames]
        dset.append(row)


def detect(stream):
    """Returns True if the given stream is valid DBF"""
    # _dbf = dbf.Table(StringIO(stream))
    try:
        if type(stream) is not bytes:
            stream = bytes(stream, "utf-8")
        dbf.Dbf(io.BytesIO(stream), readOnly=True)
        return True
    except Exception:
        return False
