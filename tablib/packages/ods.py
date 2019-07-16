# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2016  Entr'ouvert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import tempfile
import zipfile

from tablib.packages import loxun
from tablib.compat import unicode

OFFICE_NS = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
TABLE_NS = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
TEXT_NS = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
XLINK_NS = 'http://www.w3.org/1999/xlink'
STYLE_NS = 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'


class ODSWorkbook(object):
    OPENED = 1
    CLOSED = 2
    INSHEET = 3
    INROW = 4

    def __init__(self, output):
        z = self.z = zipfile.ZipFile(output, 'w')
        z.writestr('mimetype', 'application/vnd.oasis.opendocument.spreadsheet')
        z.writestr('META-INF/manifest.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
 <manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>
 <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="META-INF/manifest.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="mimetype" manifest:media-type="text/plain"/>
</manifest:manifest>''')
        z.writestr('styles.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
</office:document-styles>''')
        self.content = tempfile.NamedTemporaryFile()
        xml = self.xmlwriter = loxun.XmlWriter(self.content, pretty=False)
        xml.addNamespace('office', OFFICE_NS)
        xml.addNamespace('style', STYLE_NS)
        xml.addNamespace('table', TABLE_NS)
        xml.addNamespace('xlink', XLINK_NS)
        xml.addNamespace('text', TEXT_NS)
        # add bold style for headers
        xml.startTag('office:document-content')
        xml.startTag('office:automatic-styles')
        xml.startTag('style:style', {
            'style:family': 'paragraph',
            'style:name': 'bold',
            'style:display-name': 'bold',
        })
        xml.tag('style:text-properties', {
            'style:font-weight-complex': 'bold',
            'style:font-weight': 'bold',
            'style:font-weight-asian': 'bold'
        })
        xml.endTag()
        xml.endTag()
        xml.startTag('office:body')
        xml.startTag('office:spreadsheet')
        self.status = self.OPENED

    def close(self):
        assert self.status == self.OPENED
        self.status = self.CLOSED
        xml = self.xmlwriter
        xml.endTag()
        xml.endTag()
        xml.endTag()
        self.z.write(self.content.name, 'content.xml')
        self.content.close()
        self.z.close()
        del self.z
        del self.xmlwriter
        del self.content

    def start_sheet(self, columns, title=None):
        assert self.status == self.OPENED
        self.status = self.INSHEET
        xml = self.xmlwriter
        attribs = {}
        if title:
            attribs['table:name'] = title
        xml.startTag('table:table', attribs)
        for i in range(columns):
            xml.tag('table:table-column')

    def end_sheet(self):
        assert self.status == self.INSHEET
        self.status = self.OPENED
        self.xmlwriter.endTag()

    def add_headers(self, headers):
        self.add_row(headers, {
            'table:style-name': 'bold',
            'table:default-cell-style-name': 'bold',
        }, hint='header')

    def add_row(self, row, attribs={}, hint=None):
        self.start_row(attribs)
        for cell in row:
            self.add_cell(cell, hint=hint)
        self.end_row()

    def start_row(self, attribs={}):
        assert self.status == self.INSHEET
        self.status = self.INROW
        self.xmlwriter.startTag('table:table-row', attribs)

    def end_row(self):
        assert self.status == self.INROW
        self.status = self.INSHEET
        self.xmlwriter.endTag()

    def add_cell(self, content, hint=None):
        assert self.status == self.INROW
        content = unicode(content)
        self.xmlwriter.startTag('table:table-cell', {
            'office:value-type': 'string',
        })
        self.xmlwriter.startTag('text:p')
        attribs = {}
        if hint == 'header':
            attribs['text:style-name'] = 'bold'
        self.xmlwriter.startTag('text:span', attribs)
        self.xmlwriter.text(content)
        self.xmlwriter.endTag()
        self.xmlwriter.endTag()
        self.xmlwriter.endTag()

    def __del__(self):
        if getattr(self, 'content', None) is not None:
            try:
                self.content.close()
            except:
                pass
