# -*- coding: utf-8 -*-

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


def import_set(in_stream):
	"""Returns dataset from YAML stream."""

	data = tablib.core.Dataset()
	data.dict = yaml.load(in_stream)

	return data