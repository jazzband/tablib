# -*- coding: utf-8 -*-
"""
    tablib.core
    ~~~~~~~~~~~

    This module implements the central tablib objects.

    :copyright: (c) 2010 by Kenneth Reitz.
    :license: MIT, see LICENSE for more details.
"""

from tablib.formats import FORMATS as formats


__title__ = 'tablib'
__version__ = '0.8.4'
__build__ = 0x000804
__author__ = 'Kenneth Reitz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2010 Kenneth Reitz'


class Dataset(object):
	"""The tablib Dataset object is the heart of tablib. It provides all core 
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
    
    
    .. admonition:: About the Format Attributes
    
        If you look at the code, the various output/import formats are not 
        defined within the itself. To add support for a new format, see 
        :ref:`Adding New Formats`.

    .. attribute:: csv

        A CSV representation of the Dataset object. The top row will contain 
        headers, if they have been set. Otherwise, the top row will contain 
        the first row of the dataset.
    
        A dataset object can also be imported by setting the `Dataset.csv` attribute: ::
    
            data = tablib.Dataset()
            data.csv = 'age, first_name, last_name\\n90, John, Adams'
    
        Import assumes (for now) that headers exist.


    .. attribute:: dict

        An native Python representation of the Dataset object. If headers have been 
        set, a list of Python dictionaries will be returned. If no headers have been
        set, a list of tuples (rows) will be returned instead.

        A dataset object can also be imported by setting the `Dataset.dict` attribute: ::
    
            data = tablib.Dataset()
            data.dict = [{'age': 90, 'first_name': 'Kenneth', 'last_name': 'Reitz'}]
 
    
    .. attribute:: xls

        An Excel Spreadsheet representation of the Dataset object, including 
        :ref:`seperators`. 

        *Note:* `Dataset.xls` contains binary data, so make sure to write in binary 
        mode::
        
            with open('output.xls', 'wb') as f:
                f.write(data.xls)


    .. attribute:: yaml

        A YAML representation of the Dataset object. If headers have been 
        set, a YAML list of objects will be returned. If no headers have 
        been set, a YAML list of lists (rows) will be returned instead.  

        A dataset object can also be imported by setting the `Dataset.json` attribute: ::

            data = tablib.Dataset()
            data.yaml = '- {age: 90, first_name: John, last_name: Adams}'

        Import assumes (for now) that headers exist.
	"""

	def __init__(self, *args, **kwargs):
		self._data = list(args)
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
			return self._data[key]


	def __setitem__(self, key, value):
		self._validate(value)
		self._data[key] = tuple(value)


	def __delitem__(self, key):
		del self._data[key]


	def __repr__(self):
		try:
			return '<%s dataset>' % (self.title.lower())
		except AttributeError:
			return '<dataset object>'

	
	@classmethod
	def _register_formats(cls):
		"""Adds format properties."""
		for fmt in formats:
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
			if self.headers:
				is_valid = (len(col) - 1) == self.height
			else:
				is_valid = (len(col) == self.height) if self.height else True
		else:
			is_valid = all((len(x)== self.width for x in self._data))

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

	
	@property
	def height(self):
		"""Returns the height of the Dataset."""
		return len(self._data)


	@property
	def width(self):
		"""Returns the width of the Dataset."""
		try:
			return len(self._data[0])
		except IndexError:
			try:
				return len(self.headers)
			except TypeError:
				return 0


	@property
	def headers(self):
		"""Headers property."""
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
		"""A JSON representation of the Dataset object. If headers have been 
        set, a JSON list of objects will be returned. If no headers have 
        been set, a JSON list of lists (rows) will be returned instead.  

        A dataset object can also be imported by setting the `Dataset.json` attribute: ::

            data = tablib.Dataset()
            data.json = '[{"last_name": "Adams","age": 90,"first_name": "John"}]'

		"""
		return self._package()

	
	@dict.setter
	def dict(self, pickle):
	    
		if not len(pickle):
			return

		# if list of rows
		if isinstance(pickle[0], list):
			self.wipe()
			for row in pickle:
				self.append(row)
		
		# if list of objects
		elif isinstance(pickle[0], dict):
			self.wipe()
			self.headers = pickle[0].keys()
			for row in pickle:
				self.append(row.values())
		else:
			raise UnsupportedFormat


	def append(self, row=None, col=None):
		"""Adds a row to the end of Dataset"""
		if row is not None:
			self._validate(row)
			self._data.append(tuple(row))
		elif col is not None:
			col = list(col)
			if self.headers:
				header = [col.pop(0)]
			else:
				header = []
			if len(col) == 1 and callable(col[0]):
				col = map(col[0], self._data)
			col = tuple(header + col)
				
			self._validate(col=col)

			if self.headers:
				# pop the first item off, add to headers
				self.headers.append(col[0])
				col = col[1:]
		
			if self.height and self.width:

				for i, row in enumerate(self._data):
					_row = list(row)
					_row.append(col[i])
					self._data[i] = tuple(_row)
			else:
				self._data = [tuple([row]) for row in col]


	def insert_separator(self, index, text='-'):
		"""Adds a separator to Dataset at given index."""

		sep = (index, text)
		self._separators.append(sep)


	def append_separator(self, text='-'):
		"""Adds a separator to Dataset."""

		# change offsets if headers are or aren't defined
		if not self.headers:
			index = self.height if self.height else 0
		else:
			index = (self.height + 1) if self.height else 1

		self.insert_separator(index, text)


	def insert(self, i, row=None):
		"""Inserts a row at given position in Dataset"""
		if row:
			self._validate(row)
			self._data.insert(i, tuple(row))
		elif col:
			pass
			
	
	def wipe(self):
		"""Erases all data from Dataset."""
		self._data = list()
		self.__headers = None


class Databook(object):
	"""A book of Dataset objects.
	   Currently, this exists only for XLS workbook support.
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
		"""Wipe book clean."""
		self._datasets = []

		
	@classmethod
	def _register_formats(cls):
		"""Adds format properties."""
		for fmt in formats:
			try:
				try:
					setattr(cls, fmt.title, property(fmt.export_book, fmt.import_book))
				except AttributeError:
					setattr(cls, fmt.title, property(fmt.export_book))
					
			except AttributeError:
				pass


	def add_sheet(self, dataset):
		"""Adds given dataset."""
		if type(dataset) is Dataset:
			self._datasets.append(dataset)
		else:
			raise InvalidDatasetType
		

	def _package(self):
		"""Packages Databook for delivery."""
		collector = []
		for dset in self._datasets:
			collector.append(dict(
				title = dset.title,
				data = dset.dict
			))
		return collector


	@property
	def size(self):
		"""The number of the Datasets within DataBook."""
		return len(self._datasets)


def detect(stream):
	"""Return (format, stream) of given stream."""
	for fmt in formats:
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

	
class UnsupportedFormat(NotImplementedError):
	"Format is not supported"
