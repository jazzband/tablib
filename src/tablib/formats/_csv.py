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

        if 'delimiter' not in kwargs:
            # Auto-detect the delimiter using the CSV Sniffer.
            # Reading a sample and then seeking back to the start lets the
            # Sniffer work on real data while keeping the stream intact for
            # the subsequent csv.reader call.  Crucially, we do NOT restrict
            # sniffing to a single delimiter so that files using non-comma
            # separators (e.g. ';', ':', '|') are imported correctly.  See #622.
            try:
                sample = in_stream.read(2048)
                dialect = csv.Sniffer().sniff(sample)
                # Only accept non-word-character delimiters (true separators
                # such as ',', ';', '|', ':', '\t').  The Sniffer occasionally
                # misidentifies a letter as a delimiter when the sample is short
                # or ambiguous; falling back to the default in that case is safer.
                if dialect.delimiter.isalpha() or dialect.delimiter.isdigit():
                    raise csv.Error("unlikely delimiter detected, falling back")
                kwargs['delimiter'] = dialect.delimiter
            except csv.Error:
                kwargs['delimiter'] = cls.DEFAULT_DELIMITER
            if hasattr(in_stream, 'seek'):
                in_stream.seek(0)

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
            # When no explicit delimiter is given, build a candidate list that
            # includes the format's own DEFAULT_DELIMITER plus common non-tab
            # separators.  For CSVFormat this covers ',', ';', ':', '|' while
            # keeping tab-delimited files out of CSV detection (tab-delimited
            # files belong to TSVFormat).  TSVFormat overrides DEFAULT_DELIMITER
            # to '\t' so it will still detect tab-delimited content correctly.
            # See #622.
            if delimiter is None:
                common = ',;:|'
                sniff_delimiters = (
                    common if cls.DEFAULT_DELIMITER in common
                    else cls.DEFAULT_DELIMITER
                )
            else:
                sniff_delimiters = delimiter
            csv.Sniffer().sniff(stream.read(2048), delimiters=sniff_delimiters)
            return True
        except Exception:
            return False
