from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import Table
from reportlab.lib.pagesizes import A4

import tablib
from tablib.compat import StringIO

title = 'pdf'
extensions = ('pdf', )

margin = 10

table_style = [
    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.Whiter(colors.black, 0.1)]),
]

header_style = [
    ('BACKGROUND', (0, 0), (-1, 0), colors.Whiter(colors.black, 0.6)),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)
]


def export_book(databook):
    elements = []

    for dataset in databook._datasets:
        data = []

        if dataset.headers is not None:
            new_header = [item if item is not None else '' for item in
                          dataset.headers]
            data.append(new_header)

        for row in dataset:
            new_row = [item if item is not None else '' for item in row]
            data.append(new_row)

        t = Table(data, hAlign='LEFT')
        # noinspection PyTypeChecker
        t.setStyle(
            (table_style + header_style) if dataset.headers is not None
            else table_style
        )

        elements.append(t)

    stringbuf = StringIO()
    doc = SimpleDocTemplate(stringbuf, pagesize=A4, leftMargin=margin,
                            topMargin=margin, rightMargin=margin,
                            bottomMargin=margin)
    doc.build(elements)
    return stringbuf.getvalue()


def export_set(dataset):
    book = tablib.Databook([dataset])
    return export_book(book)