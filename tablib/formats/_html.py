# -*- coding: utf-8 -*-

""" Tablib - HTML export support.
"""

import sys

if sys.version_info[0] > 2:
    from io import BytesIO as StringIO
    from tablib.packages import markup3 as markup
else:
    from cStringIO import StringIO
    from tablib.packages import markup
import bs4

import tablib
from tablib.compat import unicode
import codecs

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


def import_set(dset, in_stream, **kwargs):
    dset.wipe()
    text = in_stream.read()
    tables = bs4.BeautifulSoup(markup=text).find_all('table')
    if len(tables) != 1:
        raise ValueError('Expected 1 table, found %s' % len(tables))
    table = tables[0]

    if table.thead.tr:
        dset.headers = [
            x.string for x in table.thead.tr.find_all('th', recursive=False)]

    # this finds rows inside <thead>, <tfoot>, <tbody> also.
    for i, row in enumerate(table.find_all('tr')):
        # skip first row if it was used for the headers
        if i == 0 and dset.headers:
            continue
        dset.append(
            [cell.get_text() for cell in row.find_all('td', recursive=False)])

    print dset

