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

    #: Delimiters considered when detecting the dialect of a CSV stream.
    CANDIDATE_DELIMITERS = (',', ';', '	', '|', ':')

    @classmethod
    def sniff_delimiter(cls, in_stream):
        """Detect the delimiter used by a CSV stream.

        Only a small set of common delimiters is considered, and the
        default comma is used whenever the dialect cannot be determined
        or only one column is present.
        """
        try:
            position = in_stream.tell()
        except (AttributeError, OSError):
            position = None

        try:
            sample = in_stream.read(2048)
        except Exception:
            return cls.DEFAULT_DELIMITER

        if position is not None:
            in_stream.seek(position)

        for candidate in cls.CANDIDATE_DELIMITERS:
            if candidate not in sample:
                continue
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=candidate)
            except Exception:
                continue
            if dialect.delimiter == candidate:
                return candidate

        return cls.DEFAULT_DELIMITER

    @classmethod
    def import_set(
            cls, dset, in_stream, headers=True, skip_lines=0, **kwargs
    ):
        """Returns dataset from CSV stream."""

        dset.wipe()

        if 'delimiter' not in kwargs and not skip_lines:
            kwargs['delimiter'] = cls.sniff_delimiter(in_stream)

        kwargs.setdefault('delimiter', cls.DEFAULT_DELIMITER)

        rows = csv.reader(in_stream, **kwargs)
        for i, row in enumerate(rows):
            if i < skip_lines:
                continue
            if i == skip_lines and headers:
                dset.headers = row
            elif row:
                if i > 0 and len(row) < dset.width:
                    row += [''] * (dset.width - len(row))
                dset.append(row)

    @classmethod
    def detect(cls, stream, delimiter=None):
        """Returns True if given stream is valid CSV."""
        try:
            csv.Sniffer().sniff(stream.read(2048), delimiters=delimiter or cls.DEFAULT_DELIMITER)
            return True
        except Exception:
            return False
