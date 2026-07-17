""" Tablib - DBF Support.
"""

__lazy_modules__ = {
    "io",
    "os",
    "tablib._vendor",
    "tempfile",
}

import io
import os
import tempfile

from .._vendor.dbfpy import dbf, dbfnew
from .._vendor.dbfpy import record as dbfrecord
from ..exceptions import HeadersNeeded


class DBFFormat:
    title = 'dbf'
    extensions = ('csv',)

    DEFAULT_ENCODING = 'utf-8'

    @classmethod
    def export_set(cls, dataset):
        """Returns DBF representation of a Dataset"""
        if dataset.headers is None:
            raise HeadersNeeded('DBF export requires headers to name the fields.')
        new_dbf = dbfnew.dbf_new()
        temp_file, temp_uri = tempfile.mkstemp()

        # create the appropriate fields based on the contents of the first row;
        # with no rows, field types cannot be inferred so default to character
        first_row = dataset[0] if dataset.height else [None] * len(dataset.headers)
        for fieldname, field_value in zip(dataset.headers, first_row):
            if type(field_value) in [int, float]:
                new_dbf.add_field(fieldname, 'N', 10, 8)
            else:
                new_dbf.add_field(fieldname, 'C', 80)

        new_dbf.write(temp_uri)

        dbf_file = dbf.Dbf(temp_uri, readOnly=0)
        for row in dataset:
            record = dbfrecord.DbfRecord(dbf_file)
            for fieldname, field_value in zip(dataset.headers, row):
                record[fieldname] = field_value
            record.store()

        dbf_file.close()
        dbf_stream = open(temp_uri, 'rb')
        stream = io.BytesIO(dbf_stream.read())
        dbf_stream.close()
        os.close(temp_file)
        os.remove(temp_uri)
        return stream.getvalue()

    @classmethod
    def import_set(cls, dset, in_stream):
        """Returns a dataset from a DBF stream."""

        dset.wipe()
        _dbf = dbf.Dbf(in_stream)
        dset.headers = _dbf.fieldNames
        for record in range(_dbf.recordCount):
            row = [_dbf[record][f] for f in _dbf.fieldNames]
            dset.append(row)

    @classmethod
    def detect(cls, stream):
        """Returns True if the given stream is valid DBF"""
        try:
            dbf.Dbf(stream, readOnly=True)
            return True
        except Exception:
            return False
