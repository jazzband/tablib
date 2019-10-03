# -*- coding: utf-8 -*-

""" Tablib - HTML export support.
"""

import sys

if sys.version_info[0] > 2:
    from io import BytesIO as StringIO
else:
    from cStringIO import StringIO

import codecs
from MarkupPy import markup
import tablib
from tablib.compat import unicode

BOOK_ENDINGS = 'h3'

title = 'html'
extensions = ('html', )


def export_set(dataset):
    """HTML representation of a Dataset."""

    stream = StringIO()

    page = markup.page()
    page.table.open()

    if dataset.headers is not None:
        new_header = [item if item is not None else '' for item in dataset.headers]

        page.thead.open()
        headers = markup.oneliner.th(new_header)
        page.tr(headers)
        page.thead.close()

    for row in dataset:
        new_row = [item if item is not None else '' for item in row]

        html_row = markup.oneliner.td(new_row)
        page.tr(html_row)

    page.table.close()

    # Allow unicode characters in output
    wrapper = codecs.getwriter("utf8")(stream)
    wrapper.writelines(unicode(page))

    return stream.getvalue().decode('utf-8')


def export_book(databook):
    """HTML representation of a Databook."""

    stream = StringIO()

    # Allow unicode characters in output
    wrapper = codecs.getwriter("utf8")(stream)

    for i, dset in enumerate(databook._datasets):
        title = (dset.title if dset.title else 'Set %s' % (i))
        wrapper.write('<%s>%s</%s>\n' % (BOOK_ENDINGS, title, BOOK_ENDINGS))
        wrapper.write(dset.html)
        wrapper.write('\n')

    return stream.getvalue().decode('utf-8')
