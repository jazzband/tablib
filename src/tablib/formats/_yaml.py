""" Tablib - YAML Support.
"""

__lazy_modules__ = {"datetime", "decimal", "uuid", "yaml"}

import datetime as dt
import decimal
from uuid import UUID

import yaml

import tablib


def _dump(data):
    class Dumper(yaml.SafeDumper):
        pass

    # Written as strings, like the JSON format does.
    for type_ in (decimal.Decimal, UUID, dt.time):
        Dumper.add_representer(type_, lambda dumper, value: dumper.represent_str(str(value)))

    return yaml.dump(
        data,
        Dumper=Dumper,
        default_flow_style=None,
        allow_unicode=True,
        sort_keys=False,
    )


class YAMLFormat:
    title = 'yaml'
    extensions = ('yaml', 'yml')

    @classmethod
    def export_set(cls, dataset):
        """Returns YAML representation of Dataset."""
        return _dump(dataset._package())

    @classmethod
    def export_book(cls, databook):
        """Returns YAML representation of Databook."""
        return _dump(databook._package())

    @classmethod
    def import_set(cls, dset, in_stream):
        """Returns dataset from YAML stream."""

        dset.wipe()
        dset.dict = yaml.safe_load(in_stream)

    @classmethod
    def import_book(cls, dbook, in_stream):
        """Returns databook from YAML stream."""

        dbook.wipe()

        for sheet in yaml.safe_load(in_stream):
            data = tablib.Dataset()
            data.title = sheet['title']
            data.dict = sheet['data']
            dbook.add_sheet(data)

    @classmethod
    def detect(cls, stream):
        """Returns True if given stream is valid YAML."""
        try:
            _yaml = yaml.safe_load(stream)
            if isinstance(_yaml, (list, tuple, dict)):
                return True
            else:
                return False
        except (yaml.parser.ParserError, yaml.reader.ReaderError,
                yaml.scanner.ScannerError):
            return False
