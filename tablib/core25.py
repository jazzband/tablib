# -*- coding: utf-8 -*-
u"""
    tablib.core
    ~~~~~~~~~~~

    This module implements the central Tablib objects.

    :copyright: (c) 2011 by Kenneth Reitz.
    :license: MIT, see LICENSE for more details.
"""

from copy import copy
from operator import itemgetter

from tablib import formats
import collections
from itertools import izip
from itertools import imap

try:
    from collections import OrderedDict
except ImportError:
    from tablib.packages.ordereddict import OrderedDict


__title__ = u'tablib'
__version__ = u'0.9.4'
__build__ = 0x000904
__author__ = u'Kenneth Reitz'
__license__ = u'MIT'
__copyright__ = u'Copyright 2011 Kenneth Reitz'
__docformat__ = u'restructuredtext'


class Row(object):
    u"""Internal Row object. Mainly used for filtering."""

    __slots__ = [u'tuple', u'_row', u'tags']

    def __init__(self, row=list(), tags=list()):
        self._row = list(row)
        self.tags = list(tags)

    def __iter__(self):
        return (col for col in self._row)

    def __len__(self):
        return len(self._row)

    def __repr__(self):
        return repr(self._row)

    def __getslice__(self, i, j):
        return self._row[i,j]

    def __getitem__(self, i):
        return self._row[i]

    def __setitem__(self, i, value):
        self._row[i] = value

    def __delitem__(self, i):
        del self._row[i]

    def __getstate__(self):
        return {slot: [getattr(self, slot) for slot in self.__slots__]}

    def __setstate__(self, state):
        for (k, v) in list(state.items()): setattr(self, k, v)

    def append(self, value):
        self._row.append(value)

    def insert(self, index, value):
        self._row.insert(index, value)

    def __contains__(self, item):
        return (item in self._row)

    @property
    def tuple(self):
        u'''Tuple representation of :class:`Row`.'''
        return tuple(self._row)

    @property
    def list(self):
        u'''List representation of :class:`Row`.'''
        return list(self._row)

    def has_tag(self, tag):
        u"""Returns true if current row contains tag."""

        if tag == None:
            return False
        elif isinstance(tag, basestring):
            return (tag in self.tags)
        else:
            return bool(len(set(tag) & set(self.tags)))
                



class Dataset(object):
    u"""The :class:`Dataset` object is the heart of Tablib. It provides all core
    functionality.

    Usually you create a :class:`Dataset` instance in your main module, and append
    rows and columns as you collect data. ::

        data = tablib.Dataset()
        data.headers = ('name', 'age')

        for (name, age) in some_collector():
            data.append((name, age))

    You can also set rows and headers upon instantiation. This is useful if dealing
    with dozens or hundres of :class:`Dataset` objects. ::

        headers = ('first_name', 'last_name')
        data = [('John', 'Adams'), ('George', 'Washington')]

        data = tablib.Dataset(*data, headers=headers)


    :param \*args: (optional) list of rows to populate Dataset
    :param headers: (optional) list strings for Dataset header row


    .. admonition:: Format Attributes Definition

     If you look at the code, the various output/import formats are not
     defined within the :class:`Dataset` object. To add support for a new format, see
     :ref:`Adding New Formats <newformats>`.

    """

    def __init__(self, *args, **kwargs):
        self._data = list(Row(arg) for arg in args)
        self.__headers = None

        # ('title', index) tuples
        self._separators = []
        
        # (column, callback) tuples
        self._formatters = []

        try:
            self.headers = kwargs[u'headers']
        except KeyError:
            self.headers = None

        try:
            self.title = kwargs[u'title']
        except KeyError:
            self.title = None

        self._register_formats()


    def __len__(self):
        return self.height


    def __getitem__(self, key):
        if isinstance(key, basestring):
            if key in self.headers:
                pos = self.headers.index(key) # get 'key' index from each data
                return [row[pos] for row in self._data]
            else:
                raise KeyError
        else:
            _results = self._data[key]
            if isinstance(_results, Row):
                return _results.tuple
            else:
                return [result.tuple for result in _results]


    def __setitem__(self, key, value):
        self._validate(value)
        self._data[key] = Row(value)


    def __delitem__(self, key):
        if isinstance(key, basestring):

            if key in self.headers:

                pos = self.headers.index(key)
                del self.headers[pos]

                for i, row in enumerate(self._data):

                    del row[pos]
                    self._data[i] = row
            else:
                raise KeyError
        else:
            del self._data[key]


    def __repr__(self):
        try:
            return u'<%s dataset>' % (self.title.lower())
        except AttributeError:
            return u'<dataset object>'


    @classmethod
    def _register_formats(cls):
        u"""Adds format properties."""
        for fmt in formats.available:
            try:
                try:
                    setattr(cls, fmt.title, property(fmt.export_set, fmt.import_set))
                except AttributeError:
                    setattr(cls, fmt.title, property(fmt.export_set))

            except AttributeError:
                pass


    def _validate(self, row=None, col=None, safety=False):
        u"""Assures size of every row in dataset is of proper proportions."""
        if row:
            is_valid = (len(row) == self.width) if self.width else True
        elif col:
            if len(col) < 1:
                is_valid = True
            else:
                is_valid = (len(col) == self.height) if self.height else True
        else:
            is_valid = all((len(x) == self.width for x in self._data))

        if is_valid:
            return True
        else:
            if not safety:
                raise InvalidDimensions
            return False


    def _package(self, dicts=True):
        u"""Packages Dataset into lists of dictionaries for transmission."""

        _data = list(self._data)
        
        # Execute formatters
        if self._formatters:
            for row_i, row in enumerate(_data):
                for col, callback in self._formatters:
                    try:                        
                        if col is None:
                            for j, c in enumerate(row):
                                _data[row_i][j] = callback(c)
                        else:
                            _data[row_i][col] = callback(row[col])
                    except IndexError:
                        raise InvalidDatasetIndex
                        

        if self.headers:
            if dicts:
                data = [OrderedDict(list(izip(self.headers, data_row))) for data_row in _data]
            else:
                data = [list(self.headers)] + list(_data)
        else:
            data = [list(row) for row in _data]

        return data


    def _clean_col(self, col):
        u"""Prepares the given column for insert/append."""

        col = list(col)

        if self.headers:
            header = [col.pop(0)]
        else:
            header = []

        if len(col) == 1 and hasattr(col[0], '__call__'):
            col = list(imap(col[0], self._data))
        col = tuple(header + col)

        return col


    @property
    def height(self):
        u"""The number of rows currently in the :class:`Dataset`.
           Cannot be directly modified.
        """
        return len(self._data)


    @property
    def width(self):
        u"""The number of columns currently in the :class:`Dataset`.
           Cannot be directly modified.
        """

        try:
            return len(self._data[0])
        except IndexError:
            try:
                return len(self.headers)
            except TypeError:
                return 0


    def _get_headers(self):
        u"""An *optional* list of strings to be used for header rows and attribute names.

        This must be set manually. The given list length must equal :class:`Dataset.width`.

        """
        return self.__headers


    def _set_headers(self, collection):
        u"""Validating headers setter."""
        self._validate(collection)
        if collection:
            try:
                self.__headers = list(collection)
            except TypeError:
                raise TypeError
        else:
            self.__headers = None

    headers = property(_get_headers, _set_headers)

    def _get_dict(self):
        u"""A native Python representation of the :class:`Dataset` object. If headers have 
        been set, a list of Python dictionaries will be returned. If no headers have been set, 
        a list of tuples (rows) will be returned instead.

        A dataset object can also be imported by setting the `Dataset.dict` attribute: ::

            data = tablib.Dataset()
            data.json = '[{"last_name": "Adams","age": 90,"first_name": "John"}]'

        """
        return self._package()


    def _set_dict(self, pickle):
        u"""A native Python representation of the Dataset object. If headers have been
        set, a list of Python dictionaries will be returned. If no headers have been
        set, a list of tuples (rows) will be returned instead.

        A dataset object can also be imported by setting the :class:`Dataset.dict` attribute. ::

            data = tablib.Dataset()
            data.dict = [{'age': 90, 'first_name': 'Kenneth', 'last_name': 'Reitz'}]

        """

        if not len(pickle):
            return

        # if list of rows
        if isinstance(pickle[0], list):
            self.wipe()
            for row in pickle:
                self.append(Row(row))

        # if list of objects
        elif isinstance(pickle[0], dict):
            self.wipe()
            self.headers = list(pickle[0].keys())
            for row in pickle:
                self.append(Row(list(row.values())))
        else:
            raise UnsupportedFormat

    dict = property(_get_dict, _set_dict)


    @property
    def xls():
        u"""An Excel Spreadsheet representation of the :class:`Dataset` object, with :ref:`seperators`. Cannot be set.

         .. admonition:: Binary Warning

             :class:`Dataset.xls` contains binary data, so make sure to write in binary mode::

                with open('output.xls', 'wb') as f:
                    f.write(data.xls)'
        """
        pass


    @property
    def csv():
        u"""A CSV representation of the :class:`Dataset` object. The top row will contain
        headers, if they have been set. Otherwise, the top row will contain
        the first row of the dataset.

        A dataset object can also be imported by setting the :class:`Dataset.csv` attribute. ::

            data = tablib.Dataset()
            data.csv = 'age, first_name, last_name\\n90, John, Adams'

        Import assumes (for now) that headers exist.
        """
        pass


    @property
    def tsv():
        u"""A TSV representation of the :class:`Dataset` object. The top row will contain
        headers, if they have been set. Otherwise, the top row will contain
        the first row of the dataset.

        A dataset object can also be imported by setting the :class:`Dataset.tsv` attribute. ::

            data = tablib.Dataset()
            data.tsv = 'age\tfirst_name\tlast_name\\n90\tJohn\tAdams'

        Import assumes (for now) that headers exist.
        """

    @property
    def yaml():
        u"""A YAML representation of the :class:`Dataset` object. If headers have been
        set, a YAML list of objects will be returned. If no headers have
        been set, a YAML list of lists (rows) will be returned instead.

        A dataset object can also be imported by setting the :class:`Dataset.json` attribute: ::

            data = tablib.Dataset()
            data.yaml = '- {age: 90, first_name: John, last_name: Adams}'

        Import assumes (for now) that headers exist.
        """
        pass


    @property
    def json():
        u"""A JSON representation of the :class:`Dataset` object. If headers have been
        set, a JSON list of objects will be returned. If no headers have
        been set, a JSON list of lists (rows) will be returned instead.

        A dataset object can also be imported by setting the :class:`Dataset.json` attribute: ::

            data = tablib.Dataset()
            data.json = '[{age: 90, first_name: "John", liast_name: "Adams"}]'

        Import assumes (for now) that headers exist.
        """

    @property
    def html():
        u"""A HTML table representation of the :class:`Dataset` object. If
        headers have been set, they will be used as table headers.

        ..notice:: This method can be used for export only.
        """
        pass


    def append(self, row=None, col=None, header=None, tags=list()):
        u"""Adds a row or column to the :class:`Dataset`.
        Usage is  :class:`Dataset.insert` for documentation.
        """

        if row is not None:
            self.insert(self.height, row=row, tags=tags)
        elif col is not None:
            self.insert(self.width, col=col, header=header)


    def insert_separator(self, index, text=u'-'):
        u"""Adds a separator to :class:`Dataset` at given index."""

        sep = (index, text)
        self._separators.append(sep)


    def append_separator(self, text=u'-'):
        u"""Adds a :ref:`seperator <seperators>` to the :class:`Dataset`."""

        # change offsets if headers are or aren't defined
        if not self.headers:
            index = self.height if self.height else 0
        else:
            index = (self.height + 1) if self.height else 1

        self.insert_separator(index, text)


    def add_formatter(self, col, handler):
        u"""Adds a :ref:`formatter` to the :class:`Dataset`.
        
        .. versionadded:: 0.9.5
           :param col: column to. Accepts index int or header str.
           :param handler: reference to callback function to execute 
           against each cell value.
        """
        
        if isinstance(col, basestring):
            if col in self.headers:
                col = self.headers.index(col) # get 'key' index from each data
            else:
                raise KeyError
        
        if not col > self.width:
            self._formatters.append((col, handler))
        else:
            raise InvalidDatasetIndex
        
        return True
        

    def insert(self, index, row=None, col=None, header=None, tags=list()):
        u"""Inserts a row or column to the :class:`Dataset` at the given index.

        Rows and columns inserted must be the correct size (height or width).

        The default behaviour is to insert the given row to the :class:`Dataset`
        object at the given index. If the ``col`` parameter is given, however,
        a new column will be insert to the :class:`Dataset` object instead.

        You can also insert a column of a single callable object, which will
        add a new column with the return values of the callable each as an
        item in the column. ::

            data.append(col=random.randint)

        See :ref:`dyncols` for an in-depth example.

        .. versionchanged:: 0.9.0
           If inserting a column, and :class:`Dataset.headers` is set, the
           header attribute must be set, and will be considered the header for
           that row.

        .. versionadded:: 0.9.0
           If inserting a row, you can add :ref:`tags <tags>` to the row you are inserting.
           This gives you the ability to :class:`filter <Dataset.filter>` your
           :class:`Dataset` later.

        """
        if row:
            self._validate(row)
            self._data.insert(index, Row(row, tags=tags))
        elif col:
            col = list(col)

            # Callable Columns...
            if len(col) == 1 and hasattr(col[0], '__call__'):
                col = list(imap(col[0], self._data))

            col = self._clean_col(col)
            self._validate(col=col)

            if self.headers:
                # pop the first item off, add to headers
                if not header:
                    raise HeadersNeeded()
                self.headers.insert(index, header)

            if self.height and self.width:

                for i, row in enumerate(self._data):

                    row.insert(index, col[i])
                    self._data[i] = row
            else:
                self._data = [Row([row]) for row in col]


    def filter(self, tag):
        u"""Returns a new instance of the :class:`Dataset`, excluding any rows
        that do not contain the given :ref:`tags <tags>`.
        """
        _dset = copy(self)
        _dset._data = [row for row in _dset._data if row.has_tag(tag)]

        return _dset


    def sort(self, col, reverse=False):
        u"""Sort a :class:`Dataset` by a specific column, given string (for
        header) or integer (for column index). The order can be reversed by
        setting ``reverse`` to ``True``. 
        Returns a new :class:`Dataset` instance where columns have been
        sorted."""
        
        if isinstance(col, basestring):

            if not self.headers:
                raise HeadersNeeded

            _sorted = sorted(self.dict, key=itemgetter(col), reverse=reverse)
            _dset = Dataset(headers=self.headers)

            for item in _sorted:
                row = [item[key] for key in self.headers]
                _dset.append(row=row)

        else:
            if self.headers:
                col = self.headers[col]

            _sorted = sorted(self.dict, key=itemgetter(col), reverse=reverse)
            _dset = Dataset(headers=self.headers)

            for item in _sorted:
                if self.headers:
                    row = [item[key] for key in self.headers]
                else:
                    row = item
                _dset.append(row=row)


        return _dset


    def transpose(self):
        u"""Transpose a :class:`Dataset`, turning rows into columns and vice
        versa, returning a new ``Dataset`` instance. The first row of the
        original instance becomes the new header row."""

        # Don't transpose if there is no data
        if not self:
            return

        _dset = Dataset()
        # The first element of the headers stays in the headers,
        # it is our "hinge" on which we rotate the data
        new_headers = [self.headers[0]] + self[self.headers[0]]

        _dset.headers = new_headers
        for column in self.headers:

            if column == self.headers[0]:
                # It's in the headers, so skip it
                continue

            # Adding the column name as now they're a regular column
            row_data = [column] + self[column]
            row_data = Row(row_data)
            _dset.append(row=row_data)

        return _dset


    def stack_rows(self, other):
        u"""Stack two :class:`Dataset` instances together by
        joining at the row level, and return new combined
        ``Dataset`` instance."""

        if not isinstance(other, Dataset):
            return

        if self.width != other.width:
            raise InvalidDimensions

        # Copy the source data
        _dset = copy(self)

        rows_to_stack = [row for row in _dset._data]
        other_rows = [row for row in other._data]

        rows_to_stack.extend(other_rows)
        _dset._data = rows_to_stack

        return _dset


    def stack_columns(self, other):
        u"""Stack two :class:`Dataset` instances together by
        joining at the column level, and return a new
        combined ``Dataset`` instance. If either ``Dataset``
        has headers set, than the other must as well."""

        if not isinstance(other, Dataset):
            return

        if self.headers or other.headers:
            if not self.headers or not other.headers:
                raise HeadersNeeded

        if self.height != other.height:
            raise InvalidDimensions

        try:
            new_headers = self.headers + other.headers
        except TypeError:
            new_headers = None

        _dset = Dataset()

        for column in self.headers:
            _dset.append(col=self[column])

        for column in other.headers:
            _dset.append(col=other[column])

        _dset.headers = new_headers

        return _dset


    def wipe(self):
        u"""Removes all content and headers from the :class:`Dataset` object."""
        self._data = list()
        self.__headers = None



class Databook(object):
    u"""A book of :class:`Dataset` objects.
    """

    def __init__(self, sets=None):

        if sets is None:
            self._datasets = list()
        else:
            self._datasets = sets

        self._register_formats()

    def __repr__(self):
        try:
            return u'<%s databook>' % (self.title.lower())
        except AttributeError:
            return u'<databook object>'


    def wipe(self):
        u"""Removes all :class:`Dataset` objects from the :class:`Databook`."""
        self._datasets = []


    @classmethod
    def _register_formats(cls):
        u"""Adds format properties."""
        for fmt in formats.available:
            try:
                try:
                    setattr(cls, fmt.title, property(fmt.export_book, fmt.import_book))
                except AttributeError:
                    setattr(cls, fmt.title, property(fmt.export_book))

            except AttributeError:
                pass


    def add_sheet(self, dataset):
        u"""Adds given :class:`Dataset` to the :class:`Databook`."""
        if type(dataset) is Dataset:
            self._datasets.append(dataset)
        else:
            raise InvalidDatasetType


    def _package(self):
        u"""Packages :class:`Databook` for delivery."""
        collector = []
        for dset in self._datasets:
            collector.append(OrderedDict(
                title = dset.title,
                data = dset.dict
            ))
        return collector


    @property
    def size(self):
        u"""The number of the :class:`Dataset` objects within :class:`Databook`."""
        return len(self._datasets)


def detect(stream):
    u"""Return (format, stream) of given stream."""
    for fmt in formats.available:
        try:
            if fmt.detect(stream):
                return (fmt, stream)
        except AttributeError:
            pass
    return (None, stream)


def import_set(stream):
    u"""Return dataset of given stream."""
    (format, stream) = detect(stream)

    try:
        data = Dataset()
        format.import_set(data, stream)
        return data

    except AttributeError, e:
        return None


class InvalidDatasetType(Exception):
    u"Only Datasets can be added to a DataBook"


class InvalidDimensions(Exception):
    u"Invalid size"
    
class InvalidDatasetIndex(Exception):
    u"Outside of Dataset size"

class HeadersNeeded(Exception):
    u"Header parameter must be given when appending a column in this Dataset."

class UnsupportedFormat(NotImplementedError):
    u"Format is not supported"
