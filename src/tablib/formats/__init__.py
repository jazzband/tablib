""" Tablib - formats
"""
from collections import OrderedDict
from functools import partialmethod
from importlib import import_module
from importlib.util import find_spec

from tablib.exceptions import UnsupportedFormat

from ._csv import CSVFormat
from ._json import JSONFormat
from ._tsv import TSVFormat

uninstalled_format_messages = {
    'cli': (
        "The 'cli' format is not available. You may want to install the tabulate "
        "package (or `pip install tablib[cli]`)."
    ),
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


def load_format_class(dotted_path):
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
        return getattr(import_module(module_path), class_name)
    except (ValueError, AttributeError) as err:
        raise ImportError("Unable to load format class '{}' ({})".format(dotted_path, err))


class FormatDescriptorBase:
    def __init__(self, key, format_or_path):
        self.key = key
        self._format_path = None
        if isinstance(format_or_path, str):
            self._format = None
            self._format_path = format_or_path
        else:
            self._format = format_or_path

    def ensure_format_loaded(self):
        if self._format is None:
            self._format = load_format_class(self._format_path)


class ImportExportBookDescriptor(FormatDescriptorBase):
    def __get__(self, obj, cls, **kwargs):
        self.ensure_format_loaded()
        return self._format.export_book(obj, **kwargs)

    def __set__(self, obj, val):
        self.ensure_format_loaded()
        return self._format.import_book(obj, val)


class ImportExportSetDescriptor(FormatDescriptorBase):
    def __get__(self, obj, cls, **kwargs):
        self.ensure_format_loaded()
        return self._format.export_set(obj, **kwargs)

    def __set__(self, obj, val):
        self.ensure_format_loaded()
        return self._format.import_set(obj, val)


class Registry:
    _formats = OrderedDict()

    def register(self, key, format_or_path):
        from tablib.core import Databook, Dataset

        # Create Databook.<format> read or read/write properties
        setattr(Databook, key, ImportExportBookDescriptor(key, format_or_path))

        # Create Dataset.<format> read or read/write properties,
        # and Dataset.get_<format>/set_<format> methods.
        setattr(Dataset, key, ImportExportSetDescriptor(key, format_or_path))
        try:
            setattr(Dataset, 'get_%s' % key, partialmethod(Dataset._get_in_format, key))
            setattr(Dataset, 'set_%s' % key, partialmethod(Dataset._set_in_format, key))
        except AttributeError:
            setattr(Dataset, 'get_%s' % key, partialmethod(Dataset._get_in_format, key))

        self._formats[key] = format_or_path

    def register_builtins(self):
        # Registration ordering matters for autodetection.
        self.register('json', JSONFormat())
        # xlsx before as xls (xlrd) can also read xlsx
        if find_spec('openpyxl'):
            self.register('xlsx', 'tablib.formats._xlsx.XLSXFormat')
        if find_spec('xlrd') and find_spec('xlwt'):
            self.register('xls', 'tablib.formats._xls.XLSFormat')
        if find_spec('yaml'):
            self.register('yaml', 'tablib.formats._yaml.YAMLFormat')
        self.register('csv', CSVFormat())
        self.register('tsv', TSVFormat())
        if find_spec('odf'):
            self.register('ods', 'tablib.formats._ods.ODSFormat')
        self.register('dbf', 'tablib.formats._dbf.DBFFormat')
        if find_spec('MarkupPy'):
            self.register('html', 'tablib.formats._html.HTMLFormat')
        self.register('jira', 'tablib.formats._jira.JIRAFormat')
        self.register('latex', 'tablib.formats._latex.LATEXFormat')
        if find_spec('pandas'):
            self.register('df', 'tablib.formats._df.DataFrameFormat')
        self.register('rst', 'tablib.formats._rst.ReSTFormat')
        if find_spec('tabulate'):
            self.register('cli', 'tablib.formats._cli.CLIFormat')

    def formats(self):
        for key, frm in self._formats.items():
            if isinstance(frm, str):
                self._formats[key] = load_format_class(frm)
            yield self._formats[key]

    def get_format(self, key):
        if key not in self._formats:
            if key in uninstalled_format_messages:
                raise UnsupportedFormat(uninstalled_format_messages[key])
            raise UnsupportedFormat("Tablib has no format '%s' or it is not registered." % key)
        if isinstance(self._formats[key], str):
            self._formats[key] = load_format_class(self._formats[key])
        return self._formats[key]


registry = Registry()
