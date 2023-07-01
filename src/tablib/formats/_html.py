""" Tablib - HTML export support.
"""
from xml.etree import ElementTree as ET


class HTMLFormat:
    BOOK_ENDINGS = 'h3'

    title = 'html'
    extensions = ('html', )

    @classmethod
    def export_set(cls, dataset):
        """HTML representation of a Dataset."""

        table = ET.Element('table')
        if dataset.headers is not None:
            head = ET.Element('thead')
            tr = ET.Element('tr')
            for header in dataset.headers:
                th = ET.Element('th')
                th.text = str(header) if header is not None else ''
                tr.append(th)
            head.append(tr)
            table.append(head)

        body = ET.Element('tbody')
        for row in dataset:
            tr = ET.Element('tr')
            for item in row:
                td = ET.Element('td')
                td.text = str(item) if item is not None else ''
                tr.append(td)
            body.append(tr)
        table.append(body)

        return ET.tostring(table, method='html', encoding='unicode')

    @classmethod
    def export_book(cls, databook):
        """HTML representation of a Databook."""

        result = ''
        for i, dset in enumerate(databook._datasets):
            title = dset.title if dset.title else f'Set {i}'
            result += f'<{cls.BOOK_ENDINGS}>{title}</{cls.BOOK_ENDINGS}>\n'
            result += dset.html
            result += '\n'

        return result
