# -*- coding: utf-8 -*-
"""
    tablib.core
    ~~~~~~~~~~~

    This module implements the central tablib objects.

    :copyright: (c) 2010 by Kenneth Reitz.
    :license: MIT, see LICENSE for more details.
"""

from copy import copy

from tablib import formats


__title__ = 'tablib'
__version__ = '0.9.1'
__build__ = 0x000901
__author__ = 'Kenneth Reitz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2010 Kenneth Reitz'

class Row(object):
	"""Internal Row object. Mainly used for filtering."""

	__slots__ = ['tuple', '_row', 'tags']

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

	def append(self, value):
		self._row.append(value)

	def insert(self, index, value):
		self._row.insert(index, value)

	def __contains__(self, item):
		return (item in self._row)

	@property
	def tuple(self):
		'''Tuple representation of :class:`Row`.'''
		return tuple(self._row)

	@property
	def list(self):
		'''List representation of :class:`Row`.'''
		return list(self._row)

	def has_tag(self, tag):
		"""Returns true if current row contains tag."""

		if tag == None:
			return False
		elif isinstance(tag, basestring):
			return tag in self.tags
		else:
			for t in tag:
				if t in self.tags:
					return True
			return False


class Dataset(object):
	"""The :class:`Dataset` object is the heart of Tablib. It provides all core 
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

		try:
			self.headers = kwargs['headers']
		except KeyError:
			self.headers = None

		try:
			self.title = kwargs['title']
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
			return '<%s dataset>' % (self.title.lower())
		except AttributeError:
			return '<dataset object>'

	
	@classmethod
	def _register_formats(cls):
		"""Adds format properties."""
		for fmt in formats.available:
			try:
				try:
					setattr(cls, fmt.title, property(fmt.export_set, fmt.import_set))
				except AttributeError:
					setattr(cls, fmt.title, property(fmt.export_set))
					
			except AttributeError:
				pass


	def _validate(self, row=None, col=None, safety=False):
		"""Assures size of every row in dataset is of proper proportions."""
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
		"""Packages Dataset into lists of dictionaries for transmission."""

		if self.headers:
			if dicts:
				data = [dict(zip(self.headers, data_row)) for data_row in self ._data]
			else:
				data = [list(self.headers)] + list(self._data)
		else:
			data = [list(row) for row in self._data]

		return data


	def _clean_col(self, col):
		"""Prepares the given column for insert/append."""
		
		col = list(col)
		
		if self.headers:
			header = [col.pop(0)]
		else:
			header = []
		
		if len(col) == 1 and callable(col[0]):
			col = map(col[0], self._data)
		col = tuple(header + col)
		
		return col

	
	@property
	def height(self):
		"""The number of rows currently in the :class:`Dataset`.
		   Cannot be directly modified.
		"""
		return len(self._data)


	@property
	def width(self):
		"""The number of columns currently in the :class:`Dataset`.
		   Cannot be directly modified.
		"""
		
		try:
			return len(self._data[0])
		except IndexError:
			try:
				return len(self.headers)
			except TypeError:
				return 0


	@property
	def headers(self):
		"""An *optional* list of strings to be used for header rows and attribute names.
        
        This must be set manually. The given list length must equal :class:`Dataset.width`.

		"""
		return self.__headers


	@headers.setter
	def headers(self, collection):
		"""Validating headers setter."""
		self._validate(collection)
		if collection:
			try:
				self.__headers = list(collection)
			except TypeError:
				raise TypeError
		else:
			self.__headers = None


	@property
	def dict(self):
		"""A JSON representation of the :class:`Dataset` object. If headers have been 
        set, a JSON list of objects will be returned. If no headers have 
        been set, a JSON list of lists (rows) will be returned instead.  

        A dataset object can also be imported by setting the `Dataset.json` attribute: ::

            data = tablib.Dataset()
            data.json = '[{"last_name": "Adams","age": 90,"first_name": "John"}]'

		"""
		return self._package()

	
	@dict.setter
	def dict(self, pickle):
		"""A native Python representation of the Dataset object. If headers have been 
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
			self.headers = pickle[0].keys()
			for row in pickle:
				self.append(Row(row.values()))
		else:
			raise UnsupportedFormat

	@property
	def xls():
		"""An Excel Spreadsheet representation of the :class:`Dataset` object, with :ref:`seperators`. Cannot be set.

	     .. admonition:: Binary Warning

	         :class:`Dataset.xls` contains binary data, so make sure to write in binary mode::

	            with open('output.xls', 'wb') as f:
	                f.write(data.xls)'
		"""
		pass

	
	@property
	def csv():
		"""A CSV representation of the :class:`Dataset` object. The top row will contain 
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
		"""A TSV representation of the :class:`Dataset` object. The top row will contain 
	    headers, if they have been set. Otherwise, the top row will contain 
	    the first row of the dataset.

	    A dataset object can also be imported by setting the :class:`Dataset.tsv` attribute. ::

	        data = tablib.Dataset()
	        data.tsv = 'age\tfirst_name\tlast_name\\n90\tJohn\tAdams'

	    Import assumes (for now) that headers exist.
		"""

	@property
	def yaml():
		"""A YAML representation of the :class:`Dataset` object. If headers have been 
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
		"""A JSON representation of the :class:`Dataset` object. If headers have been 
	    set, a JSON list of objects will be returned. If no headers have 
	    been set, a JSON list of lists (rows) will be returned instead.  

	    A dataset object can also be imported by setting the :class:`Dataset.json` attribute: ::

	        data = tablib.Dataset()
	        data.json = '[{age: 90, first_name: "John", liast_name: "Adams"}]'

	    Import assumes (for now) that headers exist.
		"""


	def append(self, row=None, col=None, header=None, tags=list()):
		"""Adds a row or column to the :class:`Dataset`.
		Usage is  :class:`Dataset.insert` for documentation.
        """

		if row is not None:
			self.insert(self.height, row=row, tags=tags)
		elif col is not None:
			self.insert(self.width, col=col, header=header)

	def insert_separator(self, index, text='-'):
		"""Adds a separator to :class:`Dataset` at given index."""

		sep = (index, text)
		self._separators.append(sep)


	def append_separator(self, text='-'):
		"""Adds a :ref:`seperator <seperators>` to the :class:`Dataset`."""

		# change offsets if headers are or aren't defined
		if not self.headers:
			index = self.height if self.height else 0
		else:
			index = (self.height + 1) if self.height else 1

		self.insert_separator(index, text)


	def insert(self, index, row=None, col=None, header=None, tags=list()):
		"""Inserts a row or column to the :class:`Dataset` at the given index. 
        
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
			if len(col) == 1 and callable(col[0]):
				col = map(col[0], self._data)

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
		"""Returns a new instance of the :class:`Dataset`, excluding any rows
		that do not contain the given :ref:`tags <tags>`. 
		"""
		_dset = copy(self)
		_dset._data = [row for row in _dset._data if row.has_tag(tag)]
		
		return _dset
	
	def wipe(self):
		"""Removes all content and headers from the :class:`Dataset` object."""
		self._data = list()
		self.__headers = None


class Databook(object):
	"""A book of :class:`Dataset` objects.
	"""

	def __init__(self, sets=[]):
		self._datasets = sets
		self._register_formats()


	def __repr__(self):
		try:
			return '<%s databook>' % (self.title.lower())
		except AttributeError:
			return '<databook object>'


	def wipe(self):
		"""Removes all :class:`Dataset` objects from the :class:`Databook`."""
		self._datasets = []

		
	@classmethod
	def _register_formats(cls):
		"""Adds format properties."""
		for fmt in formats.available:
			try:
				try:
					setattr(cls, fmt.title, property(fmt.export_book, fmt.import_book))
				except AttributeError:
					setattr(cls, fmt.title, property(fmt.export_book))
					
			except AttributeError:
				pass


	def add_sheet(self, dataset):
		"""Adds given :class:`Dataset` to the :class:`Databook`."""
		if type(dataset) is Dataset:
			self._datasets.append(dataset)
		else:
			raise InvalidDatasetType
		

	def _package(self):
		"""Packages :class:`Databook` for delivery."""
		collector = []
		for dset in self._datasets:
			collector.append(dict(
				title = dset.title,
				data = dset.dict
			))
		return collector


	@property
	def size(self):
		"""The number of the :class:`Dataset` objects within :class:`Databook`."""
		return len(self._datasets)


def detect(stream):
	"""Return (format, stream) of given stream."""
	for fmt in formats.available:
		try:
			if fmt.detect(stream):
				return (fmt, stream) 
		except AttributeError:
			pass 
	return (None, stream)
	
	
def import_set(stream):
	"""Return dataset of given stream."""
	(format, stream) = detect(stream)

	try:
		data = Dataset()
		format.import_set(data, stream)
		return data
		
	except AttributeError, e:
		return None


class InvalidDatasetType(Exception):
	"Only Datasets can be added to a DataBook"


class InvalidDimensions(Exception):
	"Invalid size"

class HeadersNeeded(Exception):
	"Header parameter must be given when appending a column in this Dataset."

class UnsupportedFormat(NotImplementedError):
	"Format is not supported"
