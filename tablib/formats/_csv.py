# -*- coding: utf-8 -*-

""" Tablib - CSV Support.
"""

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


def import_set(dset, in_stream, headers=True):
	"""Returns dataset from CSV stream."""

	dset.wipe()

	rows = csv.reader(in_stream.split())
	for i, row in enumerate(rows):

		if (i == 0) and (headers):
			dset.headers = row
		else:
			dset.append(row)
