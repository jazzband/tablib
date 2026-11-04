""" Tablib - *SV Support.
"""

__lazy_modules__ = {"csv", "io"}

import csv
from io import StringIO


class CSVFormat:
    title = 'csv'
    extensions = ('csv',)

    DEFAULT_DELIMITER = ','

    @classmethod
    def export_stream_set(cls, dataset, **kwargs):
        """Returns CSV representation of Dataset as file-like."""
        stream = StringIO()

        kwargs.setdefault('delimiter', cls.DEFAULT_DELIMITER)

        _csv = csv.writer(stream, **kwargs)

        for row in dataset._package(dicts=False):
            _csv.writerow(row)

        stream.seek(0)
        return stream

    @classmethod
    def export_set(cls, dataset, **kwargs):
        """Returns CSV representation of Dataset."""
        stream = cls.export_stream_set(dataset, **kwargs)
        return stream.getvalue()

    @classmethod
    def import_set(cls, dset, in_stream, headers=True, skip_lines=0, **kwargs):
        """Returns dataset from CSV stream."""

        dset.wipe()

        kwargs.setdefault('delimiter', cls.DEFAULT_DELIMITER)

        rows = csv.reader(in_stream, **kwargs)

        header_row = None
        data_rows = []
        for i, row in enumerate(rows):
            if i < skip_lines:
                continue
            if i == skip_lines and headers:
                header_row = row
            elif row:
                data_rows.append(row)

        # Ragged rows are normalized to the width of the widest row by filling
        # in empty elements, not just to the width of the header row (issue #226).
        width = max((len(r) for r in data_rows), default=0)
        if header_row is not None:
            width = max(width, len(header_row))
            dset.headers = header_row + [''] * (width - len(header_row))

        for row in data_rows:
            if len(row) < width:
                row = row + [''] * (width - len(row))
            dset.append(row)

    @classmethod
    def detect(cls, stream, delimiter=None):
        """Returns True if given stream is valid CSV."""
        try:
            csv.Sniffer().sniff(stream.read(2048), delimiters=delimiter or cls.DEFAULT_DELIMITER)
            return True
        except Exception:
            return False
