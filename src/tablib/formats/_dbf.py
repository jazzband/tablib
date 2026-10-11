""" Tablib - DBF Support.
"""

__lazy_modules__ = {
    "io",
    "os",
    "tablib._vendor",
    "tablib.core",
    "tempfile",
}

import io
import os
import tempfile

from .._vendor.dbfpy import dbf, dbfnew
from .._vendor.dbfpy import record as dbfrecord
from ..core import Dataset, Row


class DBFFormat:
    title = 'dbf'
    extensions = ('csv',)

    DEFAULT_ENCODING = 'utf-8'

    @classmethod
    def export_set(cls, dataset):
        """Returns DBF representation of a Dataset"""
        new_dbf = dbfnew.dbf_new()
        temp_file, temp_uri = tempfile.mkstemp()

        # create the appropriate fields based on the contents of the first row
        first_row = dataset[0]
        for fieldname, field_value in zip(dataset.headers, first_row):
            if type(field_value) in [int, float]:
                new_dbf.add_field(fieldname, 'N', 10, 8)
            else:
                new_dbf.add_field(fieldname, 'C', 80)

        new_dbf.write(temp_uri)

        dbf_file = dbf.Dbf(temp_uri, readOnly=0)
        indexes = None
        # Only validate/cache when there is enough lookup work to amortize it.
        # These conservative size cutoffs come from paired benchmarks.
        if (
            type(dataset) is Dataset
            and type(dataset.headers) is list
            and type(dataset._data) is list
            and len(dataset.headers) >= 10
            and (
                len(dataset._data) >= 100
                or (len(dataset.headers) >= 20 and len(dataset._data) >= 10)
            )
            and all(type(name) is str for name in dataset.headers)
            and all(
                type(row) is Row
                and type(row._row) is list
                and all(
                    type(value) in (str, bytes, int, float, bool, type(None))
                    for value in row._row
                )
                for row in dataset._data
            )
        ):
            first_indexes = {}
            for index, name in enumerate(dbf_file.fieldNames):
                first_indexes.setdefault(name, index)
            if all(name.upper() in first_indexes for name in dataset.headers):
                indexes = [first_indexes[name.upper()] for name in dataset.headers]
        for row in dataset:
            record = dbfrecord.DbfRecord(dbf_file)
            if indexes is None:
                for fieldname, field_value in zip(dataset.headers, row):
                    record[fieldname] = field_value
            else:
                for index, field_value in zip(indexes, row):
                    record.fieldData[index] = field_value
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
        # A BytesIO stream has stable reads. Custom streams retain the original
        # per-field reads, including any side effects they may have.
        if (
            type(in_stream) is io.BytesIO
            and type(dset) is Dataset
            and _dbf.recordCount > 0
            and dset.headers is not None
            and (
                len(dset.headers) >= 2
                or (len(dset.headers) == 1 and _dbf.recordCount >= 16)
            )
        ):
            names = _dbf.fieldNames
            first_indexes = {}
            for index, name in enumerate(names):
                first_indexes.setdefault(name, index)
            indexes = [first_indexes[name.upper()] for name in names]
            for index in range(_dbf.recordCount):
                record = _dbf[index]
                row = [record[field] for field in indexes]
                dset.append(row)
            return
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
