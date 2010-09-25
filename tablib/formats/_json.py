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


def detect(contents):
	"""Return True if contets are JSON."""
	return False


def import_set(in_stream):
	"""Returns dataset from JSON stream."""
	data = tablib.core.Dataset()
	data.dict = json.loads(in_stream)

	return data

