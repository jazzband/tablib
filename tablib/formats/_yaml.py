# -*- coding: utf-8 -*-

""" Tablib - YAML Support.
"""

try:
	import yaml
except ImportError:
	import tablib.packages.yaml as yaml

import tablib



title = 'yaml'
extentions = ('yaml', 'yml')



def export_set(dataset):
	"""Returns YAML representation of Dataset."""
	return yaml.dump(dataset.dict)


def export_book(databook):
	"""Returns YAML representation of Databook."""
	return yaml.dump(databook._package())


def import_set(dset, in_stream):
	"""Returns dataset from YAML stream."""

	dset.wipe()
	dset.dict = yaml.load(in_stream)


def import_book(dbook, in_stream):
	"""Returns databook from YAML stream."""

	dbook.wipe()

	for sheet in yaml.load(in_stream):
		data = tablib.core.Dataset()
		data.title = sheet['title']
		data.dict = sheet['data']
		dbook.add_sheet(data)
		
def detect(stream):
	"""Returns True if given stream is valid YAML."""
	try:
		_yaml = yaml.load(stream)
		if isinstance(_yaml, (list, tuple, dict)):
			return True
		else:
			return False
	except yaml.parser.ParserError:
		return False