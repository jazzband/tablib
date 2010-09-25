# -*- coding: utf-8 -*-

import cStringIO
import csv
import os

import simplejson as json

import tablib


title = 'csv'
extentions = ('csv',)



def export_set(dataset):
	"""Returns CSV representation of Dataset."""
	stream = cStringIO.StringIO()
	_csv = csv.writer(stream)

	for row in dataset._package(dicts=False):
		_csv.writerow(row)

	return stream.getvalue()


def import_set(in_stream, headers=True):
	"""Returns dataset from CSV stream."""

	data = tablib.core.Dataset()

	rows = csv.reader(in_stream.split())
	for i, row in enumerate(rows):

		if (i == 1) and (headers):
			data.headers = row
		else:
			data.append(row)

	return data