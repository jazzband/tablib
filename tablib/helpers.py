# -*- coding: utf-8 -*-

import sys


class Struct(object):
	"""Your attributes are belong to us."""
	
	def __init__(self, **entries): 
		self.__dict__.update(entries)
		
	def __getitem__(self, key):
		return getattr(self, key, None)


def piped():
	"""Returns piped input via stdin, else False."""
	with sys.stdin as stdin:
		# TTY is only way to detect if stdin contains data
		return stdin.read() if not stdin.isatty() else None

