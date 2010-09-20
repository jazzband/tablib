# -*- coding: utf-8 -*-

# _____         ______  ______        _________
# __  /_______ ____  /_ ___  /_ _____ ______  /
# _  __/_  __ `/__  __ \__  __ \_  _ \_  __  / 
# / /_  / /_/ / _  /_/ /_  /_/ //  __// /_/ /  
# \__/  \__,_/  /_.___/ /_.___/ \___/ \__,_/   


import csv
import cStringIO
import random

import simplejson as json
import xlwt
import yaml

from helpers import *


# __all__ = ['Dataset', 'DataBook']

__name__ = 'tablib'
__version__ = '0.6.4'
__build__ = 0x000604
__author__ = 'Kenneth Reitz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2010 Kenneth Reitz'


class Dataset(object):
	"""Epic Tabular-Dataset object. """

	def __init__(self, *args, **kwargs):
		self._data = None
		self._saved_file = None
		self._saved_format = None
		self._data = list(args)
		self.__headers = None

		try:
			self.headers = kwargs['headers']
		except KeyError, why:
			self.headers = None

		try:
			self.title = kwargs['title']
		except KeyError, why:
			self.title = None


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
		except IndexError, why:
			try:
				return len(self.headers)
			except TypeError, e:
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
			except TypeError, why:
				raise TypeError
		else:
			self.__headers = None



	@property
	def dict(self):
		"""Returns python dict of Dataset."""
		return self._package()


	@property
	def json(self):
		"""Returns JSON representation of Dataset."""
		return json.dumps(self.dict)


	@property
	def yaml(self):
		"""Returns YAML representation of Dataset."""
		return yaml.dump(self.dict)


	@property
	def csv(self):
		"""Returns CSV representation of Dataset."""
		stream = cStringIO.StringIO()
		_csv = csv.writer(stream)

		for row in self._package(dicts=False):
			_csv.writerow(row)

		return stream.getvalue()


	@property
	def xls(self):
		"""Returns XLS representation of Dataset."""
		stream = cStringIO.StringIO()

		wb = xlwt.Workbook()
		ws = wb.add_sheet(self.title if self.title else 'Tabbed Dataset')
		for i, row in enumerate(self._package(dicts=False)):
			for j, col in enumerate(row):
				ws.write(i, j, col.decode('utf8'))

		wb.save(stream)
		return stream.getvalue()


	def append(self, row=None, col=None):
		"""Adds a row to the end of Dataset"""
		if row:
			self._validate(row)
			self._data.append(tuple(row))
		elif col:
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


	def insert(self, i, row=None, col=None):
		"""Inserts a row at given position in Dataset"""
		if row:
			self._validate(row)
			self._data.insert(i, tuple(row))
		elif col:
			pass


class DataBook(object):
	"""A book of Dataset objects.
	   Currently, this exists only for XLS workbook support.
	"""

	def __init__(self, sets=[]):
		self._datasets = sets


	def __repr__(self):
		try:
			return '<%s databook>' % (self.title.lower())
		except AttributeError:
			return '<databook object>'


	def add_sheet(self, dataset):
		"""Add given dataset ."""
		if type(dataset) is Dataset:
			self._datasets.append(dataset)
		else:
			raise InvalidDatasetType


	def _package(self):
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


	@property
	def xls(self):
		"""Returns XLS representation of DataBook."""

		stream = cStringIO.StringIO()
		wb = xlwt.Workbook()

		for i, dset in enumerate(self._datasets):
			ws = wb.add_sheet(dset.title if dset.title else 'Sheet%s' % (i))

			#for row in self._package(dicts=False):
			for i, row in enumerate(dset._package(dicts=False)):
				for j, col in enumerate(row):
					ws.write(i, j, str(col))

		wb.save(stream)
		return stream.getvalue()

	
	@property
	def json(self):
		"""Returns JSON representation of Databook."""

		return json.dumps(self._package())


	@property
	def yaml(self):
		"""Returns YAML representation of Databook."""

		return yaml.dump(self._package())



class InvalidDatasetType(Exception):
	"Only Datasets can be added to a DataBook"


class InvalidDimensions(Exception):
	"Invalid size"

	
class UnsupportedFormat(NotImplementedError):
	"Format is not supported"
