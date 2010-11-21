# -*- coding: utf-8 -*-

""" Tablib - HTML export support.
"""

from StringIO import StringIO

from tablib.packages import markup
import tablib

title = 'html'
extentions = ('html', )

def export_set(dataset):
	"""HTML representation of a Dataset."""

	stream = StringIO()

	page = markup.page()
	page.table.open()

	if dataset.headers is not None:
		page.thead.open()
		headers = markup.oneliner.th(dataset.headers)
		page.tr(headers)
		page.thead.close()

	for row in dataset:
		html_row = markup.oneliner.td(row)
		page.tr(html_row)

	page.table.close()

	stream.writelines(str(page))

	return stream.getvalue()

