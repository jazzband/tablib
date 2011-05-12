# file openpyxl/writer/excel.py

# Copyright (c) 2010 openpyxl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: Eric Gazoni

"""Write a .xlsx file."""

# Python stdlib imports
from zipfile import ZipFile, ZIP_DEFLATED
from ....compat import BytesIO as StringIO

# package imports
from ..shared.ooxml import ARC_SHARED_STRINGS, ARC_CONTENT_TYPES, \
        ARC_ROOT_RELS, ARC_WORKBOOK_RELS, ARC_APP, ARC_CORE, ARC_THEME, \
        ARC_STYLE, ARC_WORKBOOK, \
        PACKAGE_WORKSHEETS, PACKAGE_DRAWINGS, PACKAGE_CHARTS
from ..writer.strings import create_string_table, write_string_table
from ..writer.workbook import write_content_types, write_root_rels, \
        write_workbook_rels, write_properties_app, write_properties_core, \
        write_workbook
from ..writer.theme import write_theme
from ..writer.styles import StyleWriter
from ..writer.drawings import DrawingWriter, ShapeWriter
from ..writer.charts import ChartWriter
from ..writer.worksheet import write_worksheet, write_worksheet_rels


class ExcelWriter(object):
    """Write a workbook object to an Excel file."""

    def __init__(self, workbook):
        self.workbook = workbook
        self.style_writer = StyleWriter(self.workbook)

    def write_data(self, archive):
        """Write the various xml files into the zip archive."""
        # cleanup all worksheets
        shared_string_table = self._write_string_table(archive)

        archive.writestr(ARC_CONTENT_TYPES, write_content_types(self.workbook))
        archive.writestr(ARC_ROOT_RELS, write_root_rels(self.workbook))
        archive.writestr(ARC_WORKBOOK_RELS, write_workbook_rels(self.workbook))
        archive.writestr(ARC_APP, write_properties_app(self.workbook))
        archive.writestr(ARC_CORE,
                write_properties_core(self.workbook.properties))
        archive.writestr(ARC_THEME, write_theme())
        archive.writestr(ARC_STYLE, self.style_writer.write_table())
        archive.writestr(ARC_WORKBOOK, write_workbook(self.workbook))

        self._write_worksheets(archive, shared_string_table, self.style_writer)

    def _write_string_table(self, archive):

        for ws in self.workbook.worksheets:
            ws.garbage_collect()
        shared_string_table = create_string_table(self.workbook)

            
        archive.writestr(ARC_SHARED_STRINGS,
                write_string_table(shared_string_table))

        for k, v in shared_string_table.items():
            shared_string_table[k] = bytes(v)
            
        return shared_string_table

    def _write_worksheets(self, archive, shared_string_table, style_writer):

        drawing_id = 1
        chart_id = 1
        shape_id = 1

        for i, sheet in enumerate(self.workbook.worksheets):
            archive.writestr(PACKAGE_WORKSHEETS + '/sheet%d.xml' % (i + 1),
                    write_worksheet(sheet, shared_string_table,
                            style_writer.get_style_by_hash()))
            if sheet._charts or sheet.relationships:
                archive.writestr(PACKAGE_WORKSHEETS +
                        '/_rels/sheet%d.xml.rels' % (i + 1),
                        write_worksheet_rels(sheet, drawing_id))
            if sheet._charts:
                dw = DrawingWriter(sheet)
                archive.writestr(PACKAGE_DRAWINGS + '/drawing%d.xml' % drawing_id,
                    dw.write())
                archive.writestr(PACKAGE_DRAWINGS + '/_rels/drawing%d.xml.rels' % drawing_id,
                    dw.write_rels(chart_id))
                drawing_id += 1

                for chart in sheet._charts:
                    cw = ChartWriter(chart)
                    archive.writestr(PACKAGE_CHARTS + '/chart%d.xml' % chart_id,
                        cw.write())

                    if chart._shapes:
                        archive.writestr(PACKAGE_CHARTS + '/_rels/chart%d.xml.rels' % chart_id,
                            cw.write_rels(drawing_id))
                        sw = ShapeWriter(chart._shapes)
                        archive.writestr(PACKAGE_DRAWINGS + '/drawing%d.xml' % drawing_id,
                            sw.write(shape_id))
                        shape_id += len(chart._shapes)
                        drawing_id += 1

                    chart_id += 1


    def save(self, filename):
        """Write data into the archive."""
        archive = ZipFile(filename, 'w', ZIP_DEFLATED)
        self.write_data(archive)
        archive.close()


def save_workbook(workbook, filename):
    """Save the given workbook on the filesystem under the name filename.

    :param workbook: the workbook to save
    :type workbook: :class:`openpyxl.workbook.Workbook`

    :param filename: the path to which save the workbook
    :type filename: string

    :rtype: bool

    """
    writer = ExcelWriter(workbook)
    writer.save(filename)
    return True


def save_virtual_workbook(workbook):
    """Return an in-memory workbook, suitable for a Django response."""
    writer = ExcelWriter(workbook)
    temp_buffer = StringIO()
    try:
        archive = ZipFile(temp_buffer, 'w', ZIP_DEFLATED)
        writer.write_data(archive)
    finally:
        archive.close()
    virtual_workbook = temp_buffer.getvalue()
    temp_buffer.close()
    return virtual_workbook
