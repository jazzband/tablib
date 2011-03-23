# -*- coding: utf-8 -*-

""" Tablib - HTML export support.
"""

import sys


if sys.version_info[0] > 2:
    from io import StringIO
    from tablib.packages import markup3 as markup
else:
    from cStringIO import StringIO
    from tablib.packages import markup

import tablib

BOOK_ENDINGS = 'h3'

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


def export_book(databook):
	"""HTML representation of a Databook."""

	stream = StringIO()

	for i, dset in enumerate(databook._datasets):
		title = (dset.title if dset.title else 'Set %s' % (i))
		stream.write('<%s>%s</%s>\n' % (BOOK_ENDINGS, title, BOOK_ENDINGS))
		stream.write(dset.html)
		stream.write('\n')

	return stream.getvalue()
