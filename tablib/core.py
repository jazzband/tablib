# -*- coding: utf-8 -*-

# _____         ______  ______        _________
# __  /_______ ____  /_ ___  /_ _____ ______  /
# _  __/_  __ `/__  __ \__  __ \_  _ \_  __  / 
# / /_  / /_/ / _  /_/ /_  /_/ //  __// /_/ /  
# \__/  \__,_/  /_.___/ /_.___/ \___/ \__,_/   


import csv

from helpers import *

__all__ = ['Dataset', 'source']

__version__ = '0.0.3'
__build__ = '0x000003'
__author__ = 'Kenneth Reitz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2010 Kenneth Reitz'



class Dataset(object):
	"""Amazing Tabular Dataset object. """

	def __init__(self, *args, **kwargs):

		self._data = [].append(args)

		try:
		    self.headers = kwargs['headers']
		except KeyError, why:
			self.headers = None

			
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
		pass


	@property
	def height(self):
		"""Returns the height of the Dataset."""
		return len(self._data)


	@property
	def width(self):
		"""Returns the width of the Dataset."""
		
		try:
		    len(self._data[0])
		except Exception, why:
		    raise why
			

	@property
	def json(self):
		if self.headers:
			pass

		
	@property
	def yaml(self):
		pass


	@property
	def csv(self):
		pass


	@property
	def xls(self):
		pass


	def append(self, row, index=None):
		pass

	def del_row(self):
		pass

	def save(self):
		pass

class InvalidDimensions(Exception):
	"Invalid size"


def source():
	"""docstring for import"""
	pass