# -*- coding: utf-8 -*-

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
	

def import_set(in_stream):
	"""Returns dataset from JSON stream."""
	
	data = tablib.core.Dataset()
	data.dict = json.loads(in_stream)

	return data


def import_book(in_stream):
	"""Returns databook from JSON stream."""

	book = tablib.core.Databook()
	for sheet in json.loads(in_stream):
		data = tablib.core.Dataset()
		data.title = sheet['title']
		data.dict = sheet['data']
		book.add_sheet(data)
	
	return book