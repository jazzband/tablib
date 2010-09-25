# -*- coding: utf-8 -*-

""" Tablib - YAML Support.
"""

import yaml
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