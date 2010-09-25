# -*- coding: utf-8 -*-

""" Tablib - JSON Support
"""

import simplejson as json
import tablib.core

title = 'json'
extentions = ('json', 'jsn')


def export_set(dataset):
	"""Returns JSON representation of Dataset."""
	return json.dumps(dataset.dict)


def export_book(databook):
	"""Returns JSON representation of Databook."""
	return json.dumps(databook._package())
	

def import_set(dset, in_stream):
	"""Returns dataset from JSON stream."""
	
	dset.wipe()
	dset.dict = json.loads(in_stream)


def import_book(dbook, in_stream):
	"""Returns databook from JSON stream."""

	dbook.wipe()
	for sheet in json.loads(in_stream):
		data = tablib.core.Dataset()
		data.title = sheet['title']
		data.dict = sheet['data']
		dbook.add_sheet(data)
