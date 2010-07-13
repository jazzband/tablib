# -*- coding: utf-8 -*-

class Object(object):
	"""Your attributes are belong to us."""
	def __init__(self, **entries): 
		self.__dict__.update(entries)
