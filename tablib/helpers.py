# -*- coding: utf-8 -*-

import sys


class Struct(object):
	"""Your attributes are belong to us."""
	
	def __init__(self, **entries): 
		self.__dict__.update(entries)
		
	def __getitem__(self, key):
		return getattr(self, key)


def piped():
	"""Returns piped input via stdin, else False"""
	with sys.stdin as stdin:
		return stdin.read() if not stdin.isatty() else None

		
def is_string(obj):
	"""Tests if an object is a string"""

	return True if type(obj).__name__ == 'str' else False