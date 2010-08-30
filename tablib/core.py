# -*- coding: utf-8 -*-

# _____         ______  ______        _________
# __  /_______ ____  /_ ___  /_ _____ ______  /
# _  __/_  __ `/__  __ \__  __ \_  _ \_  __  / 
# / /_  / /_/ / _  /_/ /_  /_/ //  __// /_/ /  
# \__/  \__,_/  /_.___/ /_.___/ \___/ \__,_/   


import csv
import os

from helpers import *
from packages import simplejson as json
from packages import xlwt

try:
    import yaml
except ImportError, why:
    from packages import yaml

	

__all__ = ['Dataset', 'source']

__version__ = '0.0.3'
__build__ = '0x000003'
__author__ = 'Kenneth Reitz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2010 Kenneth Reitz'


FILE_EXTENTIONS = ('csv', 'json', 'xls', 'yaml')



class Dataset(object):
	"""Amazing Tabular Dataset object. """

	def __init__(self, *args, **kwargs):
		self._data = None
		self._saved_file = None
		self._saved_format = None


		self._data = list(args)

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

		if is_string(key):
			if key in self.headers:
				pos = self.headers.index(key) # get 'key' index from each data
				return [row[pos] for row in self._data]
			else:
				raise KeyError
		else:
			return self._data[key]


	def __setitem__(self, key, value):
		self.validate(value)
		self._data[key] = value


	def __delitem__(self, key):
		del self._data[key]

		
	def __repr__(self):
		if self.title:
			return '<%s dataset>' % (self.title.lower())
		else:
			return '<dataset object>'


	def validate(self, row=None, safety=False):
		"""Assures size of every row in dataset is of proper proportions."""
		if row:
			is_valid = (len(row) == self.width) if self.width else True
		else:
			is_valid = all((len(x)== self.width for x in self._data))

		if is_valid:
			return True

		else:
			if not safety:
				raise InvalidDimensions
			return False
	
	def digest(self):
		"""Retruns digest information of dataset in human-readable format."""

		digest_text = ''
		
		if self.title:
			digest_text += 'Title: %s \n' % (self.title)
		if self.headers:
			digest_text += 'Headers: %s\n' % [self.headers]

		digest_text += 'Height: %s\nWidth: %s\n' % (self.height, self.width)


		return digest_text


	@property
	def height(self):
		"""Returns the height of the Dataset."""
		return len(self._data)


	@property
	def width(self):
		"""Returns the width of the Dataset."""
		
		try:
		    return len(self._data[0])
		except KeyError, why:
		    return 0
			

	@property
	def json(self):
		if self.headers:
			pass

		
	@property
	def yaml(self):
		# TODO: YAML Export
		pass


	@property
	def csv(self):
		# TODO: CSV Export
		pass


	@property
	def xls(self):
		# TODO: XLS Export
		pass


	def append(self, row, index=None):
		# todo: impliment index
		self.validate(row)
		self._data.append(row)

		
	def sort_by(self, key):
		"""SORTS datastet by given key"""
		# todo: accpept string if headers, or index nubmer
		pass


	def save(self, filename=None, format=None):

		if not format:
			# set format from filename
#			format = filename
			pass
			
		if format not in FILE_EXTENTIONS:
			raise UnsupportedFormat
			

		# note export format
		# open file, save the bitch


class InvalidDimensions(Exception):
	"Invalid size"


class UnsupportedFormat(NotImplemented):
	"Format is not supported"


	
def source(io_string=None, filename=None):
	"""docstring for import"""
	#open by filename
	pass