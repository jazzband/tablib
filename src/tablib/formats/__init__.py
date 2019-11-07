""" Tablib - formats
"""
from collections import OrderedDict
from functools import partialmethod
from importlib.util import find_spec

from tablib.exceptions import UnsupportedFormat

from ._csv import CSVFormat
from ._dbf import DBFFormat
from ._df import DataFrameFormat
from ._html import HTMLFormat
from ._jira import JIRAFormat
from ._json import JSONFormat
from ._latex import LATEXFormat
from ._ods import ODSFormat
from ._rst import ReSTFormat
from ._tsv import TSVFormat
from ._xls import XLSFormat
from ._xlsx import XLSXFormat
from ._yaml import YAMLFormat

uninstalled_format_messages = {
    'df': (
        "The 'df' format is not available. You may want to install the pandas "
        "package (or `pip install tablib[pandas]`)."
    ),
    'html': (
        "The 'html' format is not available. You may want to install the MarkupPy "
        "package (or `pip install tablib[html]`)."
    ),
    'ods': (
        "The 'ods' format is not available. You may want to install the odfpy "
        "package (or `pip install tablib[ods]`)."
    ),
    'xls': (
        "The 'xls' format is not available. You may want to install the xlrd and "
        "xlwt packages (or `pip install tablib[xls]`)."
    ),
    'xlsx': (
        "The 'xlsx' format is not available. You may want to install the openpyxl "
        "package (or `pip install tablib[xlsx]`)."
    ),
    'yaml': (
        "The 'yaml' format is not available. You may want to install the pyyaml "
        "package (or `pip install tablib[yaml]`)."
    ),
}


class Registry:
    _formats = OrderedDict()

    def register(self, key, format_):
        from tablib.core import Databook, Dataset

        # Create Databook.<format> read or read/write properties 
        try:
            setattr(Databook, format_.title, property(format_.export_book, format_.import_book))
        except AttributeError:
            try:
                setattr(Databook, format_.title, property(format_.export_book))
            except AttributeError:
                pass

        # Create Dataset.<format> read or read/write properties,
        # and Dataset.get_<format>/set_<format> methods.
        try:
            try:
                setattr(Dataset, format_.title, property(format_.export_set, format_.import_set))
                setattr(Dataset, 'get_%s' % format_.title, partialmethod(Dataset._get_in_format, format_))
                setattr(Dataset, 'set_%s' % format_.title, partialmethod(Dataset._set_in_format, format_))
            except AttributeError:
                setattr(Dataset, format_.title, property(format_.export_set))
                setattr(Dataset, 'get_%s' % format_.title, partialmethod(Dataset._get_in_format, format_))

        except AttributeError:
            raise Exception("Your format class should minimally implement the export_set interface.")

        self._formats[key] = format_

    def register_builtins(self):
        # Registration ordering matters for autodetection.
        self.register('json', JSONFormat())
        # xlsx before as xls (xlrd) can also read xlsx
        if find_spec('openpyxl'):
            self.register('xlsx', XLSXFormat())
        if find_spec('xlrd') and find_spec('xlwt'):
            self.register('xls', XLSFormat())
        if find_spec('yaml'):
            self.register('yaml', YAMLFormat())
        self.register('csv', CSVFormat())
        self.register('tsv', TSVFormat())
        if find_spec('odf'):
            self.register('ods', ODSFormat())
        self.register('dbf', DBFFormat())
        if find_spec('MarkupPy'):
            self.register('html', HTMLFormat())
        self.register('jira', JIRAFormat())
        self.register('latex', LATEXFormat())
        if find_spec('pandas'):
            self.register('df', DataFrameFormat())
        self.register('rst', ReSTFormat())

    def formats(self):
        for frm in self._formats.values():
            yield frm

    def get_format(self, key):
        if key not in self._formats:
            if key in uninstalled_format_messages:
                raise UnsupportedFormat(uninstalled_format_messages[key])
            raise UnsupportedFormat("Tablib has no format '%s' or it is not registered." % key)
        return self._formats[key]


registry = Registry()
