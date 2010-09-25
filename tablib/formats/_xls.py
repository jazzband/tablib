# -*- coding: utf-8 -*-

""" Tablib - XLS Support.
"""

import xlwt
import cStringIO


title = 'xls'
extentions = ('xls',)


def export_set(dataset):
	"""Returns XLS representation of Dataset."""

	wb = xlwt.Workbook(encoding='utf8')
	ws = wb.add_sheet(dataset.title if dataset.title else 'Tabbed Dataset')

	for i, row in enumerate(dataset._package(dicts=False)):
		for j, col in enumerate(row):
			ws.write(i, j, col)

	stream = cStringIO.StringIO()
	wb.save(stream)
	return stream.getvalue()


def export_book(databook):
	"""Returns XLS representation of DataBook."""

	wb = xlwt.Workbook(encoding='utf8')

	for i, dset in enumerate(databook._datasets):
		ws = wb.add_sheet(dset.title if dset.title else 'Sheet%s' % (i))

		#for row in self._package(dicts=False):
		for i, row in enumerate(dset._package(dicts=False)):
			for j, col in enumerate(row):
				ws.write(i, j, col)


	stream = cStringIO.StringIO()
	wb.save(stream)
	return stream.getvalue()