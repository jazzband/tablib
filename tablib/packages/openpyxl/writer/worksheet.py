# file openpyxl/writer/worksheet.py

# Copyright (c) 2010-2011 openpyxl
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
# @author: see AUTHORS file

"""Write worksheets to xml representations."""

# Python stdlib imports
try:
    # Python 2
    from StringIO import StringIO  # cStringIO doesn't handle unicode
    BytesIO = StringIO
except ImportError:
    # Python 3
    from io import BytesIO, StringIO

try:
    # Python 2
    isinstance(1, long)
except NameError:
    # Python 3, all ints are long
    long = int

# package imports
import decimal
from openpyxl.cell import coordinate_from_string, column_index_from_string
from openpyxl.shared.xmltools import Element, SubElement, XMLGenerator, \
        get_document_content, start_tag, end_tag, tag
from openpyxl.shared.compat.itertools import iteritems, iterkeys


def row_sort(cell):
    """Translate column names for sorting."""
    return column_index_from_string(cell.column)


def write_worksheet(worksheet, string_table, style_table):
    """Write a worksheet to an xml file."""
    xml_file = StringIO()
    doc = XMLGenerator(out=xml_file, encoding='utf-8')
    start_tag(doc, 'worksheet',
            {'xml:space': 'preserve',
            'xmlns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'xmlns:r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'})
    start_tag(doc, 'sheetPr')
    tag(doc, 'outlinePr',
            {'summaryBelow': '%d' % (worksheet.show_summary_below),
            'summaryRight': '%d' % (worksheet.show_summary_right)})
    if worksheet.page_setup.fitToPage:
        tag(doc, 'pageSetUpPr', {'fitToPage':'1'})
    end_tag(doc, 'sheetPr')
    tag(doc, 'dimension', {'ref': '%s' % worksheet.calculate_dimension()})
    write_worksheet_sheetviews(doc, worksheet)
    tag(doc, 'sheetFormatPr', {'defaultRowHeight': '15'})
    write_worksheet_cols(doc, worksheet)
    write_worksheet_data(doc, worksheet, string_table, style_table)
    if worksheet.auto_filter:
        tag(doc, 'autoFilter', {'ref': worksheet.auto_filter})
    write_worksheet_mergecells(doc, worksheet)
    write_worksheet_datavalidations(doc, worksheet)
    write_worksheet_hyperlinks(doc, worksheet)

    options = worksheet.page_setup.options
    if options:
        tag(doc, 'printOptions', options)

    margins = worksheet.page_margins.margins
    if margins:
        tag(doc, 'pageMargins', margins)

    setup = worksheet.page_setup.setup
    if setup:
        tag(doc, 'pageSetup', setup)

    if worksheet.header_footer.hasHeader() or worksheet.header_footer.hasFooter():
        start_tag(doc, 'headerFooter')
        if worksheet.header_footer.hasHeader():
            tag(doc, 'oddHeader', None, worksheet.header_footer.getHeader())
        if worksheet.header_footer.hasFooter():
            tag(doc, 'oddFooter', None, worksheet.header_footer.getFooter())
        end_tag(doc, 'headerFooter')

    if worksheet._charts or worksheet._images:
        tag(doc, 'drawing', {'r:id':'rId1'})
    end_tag(doc, 'worksheet')
    doc.endDocument()
    xml_string = xml_file.getvalue()
    xml_file.close()
    return xml_string

def write_worksheet_sheetviews(doc, worksheet):
    start_tag(doc, 'sheetViews')
    start_tag(doc, 'sheetView', {'workbookViewId': '0'})
    selectionAttrs = {}
    topLeftCell = worksheet.freeze_panes
    if topLeftCell:
        colName, row = coordinate_from_string(topLeftCell)
        column = column_index_from_string(colName)
        pane = 'topRight'
        paneAttrs = {}
        if column > 1:
            paneAttrs['xSplit'] = str(column - 1)
        if row > 1:
            paneAttrs['ySplit'] = str(row - 1)
            pane = 'bottomLeft'
            if column > 1:
                pane = 'bottomRight'
        paneAttrs.update(dict(topLeftCell=topLeftCell,
                              activePane=pane,
                              state='frozen'))
        tag(doc, 'pane', paneAttrs)
        selectionAttrs['pane'] = pane
        if row > 1 and column > 1:
            tag(doc, 'selection', {'pane': 'topRight'})
            tag(doc, 'selection', {'pane': 'bottomLeft'})

    selectionAttrs.update({'activeCell': worksheet.active_cell,
                           'sqref': worksheet.selected_cell})

    tag(doc, 'selection', selectionAttrs)
    end_tag(doc, 'sheetView')
    end_tag(doc, 'sheetViews')


def write_worksheet_cols(doc, worksheet):
    """Write worksheet columns to xml."""
    if worksheet.column_dimensions:
        start_tag(doc, 'cols')
        for column_string, columndimension in \
                iteritems(worksheet.column_dimensions):
            col_index = column_index_from_string(column_string)
            col_def = {}
            col_def['collapsed'] = str(columndimension.style_index)
            col_def['min'] = str(col_index)
            col_def['max'] = str(col_index)
            if columndimension.width != \
                    worksheet.default_column_dimension.width:
                col_def['customWidth'] = 'true'
            if not columndimension.visible:
                col_def['hidden'] = 'true'
            if columndimension.outline_level > 0:
                col_def['outlineLevel'] = str(columndimension.outline_level)
            if columndimension.collapsed:
                col_def['collapsed'] = 'true'
            if columndimension.auto_size:
                col_def['bestFit'] = 'true'
            if columndimension.width > 0:
                col_def['width'] = str(columndimension.width)
            else:
                col_def['width'] = '9.10'
            tag(doc, 'col', col_def)
        end_tag(doc, 'cols')


def write_worksheet_data(doc, worksheet, string_table, style_table):
    """Write worksheet data to xml."""
    start_tag(doc, 'sheetData')
    max_column = worksheet.get_highest_column()
    style_id_by_hash = style_table
    cells_by_row = {}
    for styleCoord in iterkeys(worksheet._styles):
        # Ensure a blank cell exists if it has a style
        worksheet.cell(styleCoord)
    for cell in worksheet.get_cell_collection():
        cells_by_row.setdefault(cell.row, []).append(cell)
    for row_idx in sorted(cells_by_row):
        row_dimension = worksheet.row_dimensions[row_idx]
        attrs = {'r': '%d' % row_idx,
                 'spans': '1:%d' % max_column}
        if not row_dimension.visible:
            attrs['hidden'] = '1'
        if row_dimension.height > 0:
            attrs['ht'] = str(row_dimension.height)
            attrs['customHeight'] = '1'
        start_tag(doc, 'row', attrs)
        row_cells = cells_by_row[row_idx]
        sorted_cells = sorted(row_cells, key=row_sort)
        for cell in sorted_cells:
            value = cell._value
            coordinate = cell.get_coordinate()
            attributes = {'r': coordinate}
            if cell.data_type != cell.TYPE_FORMULA:
                attributes['t'] = cell.data_type
            if coordinate in worksheet._styles:
                attributes['s'] = '%d' % style_id_by_hash[
                        hash(worksheet._styles[coordinate])]

            if value in ('', None):
                tag(doc, 'c', attributes)
            else:
                start_tag(doc, 'c', attributes)
                if cell.data_type == cell.TYPE_STRING:
                    tag(doc, 'v', body='%s' % string_table[value])
                elif cell.data_type == cell.TYPE_FORMULA:
                    tag(doc, 'f', body='%s' % value[1:])
                    tag(doc, 'v')
                elif cell.data_type == cell.TYPE_NUMERIC:
                    if isinstance(value, (long, decimal.Decimal)):
                        func = str
                    else:
                        func = repr
                    tag(doc, 'v', body=func(value))
                elif cell.data_type == cell.TYPE_BOOL:
                    tag(doc, 'v', body='%d' % value)
                else:
                    tag(doc, 'v', body='%s' % value)
                end_tag(doc, 'c')
        end_tag(doc, 'row')
    end_tag(doc, 'sheetData')


def write_worksheet_mergecells(doc, worksheet):
    """Write merged cells to xml."""
    if len(worksheet._merged_cells) > 0:
        start_tag(doc, 'mergeCells', {'count': str(len(worksheet._merged_cells))})
        for range_string in worksheet._merged_cells:
            attrs = {'ref': range_string}
            tag(doc, 'mergeCell', attrs)
        end_tag(doc, 'mergeCells')

def write_worksheet_datavalidations(doc, worksheet):
    """ Write data validation(s) to xml."""
    # Filter out "empty" data-validation objects (i.e. with 0 cells)
    required_dvs = [x for x in worksheet._data_validations
                    if len(x.cells) or len(x.ranges)]
    count = len(required_dvs)
    if count == 0:
        return

    start_tag(doc, 'dataValidations', {'count': str(count)})
    for data_validation in required_dvs:
        start_tag(doc, 'dataValidation', data_validation.generate_attributes_map())
        if data_validation.formula1:
            tag(doc, 'formula1', body=data_validation.formula1)
        if data_validation.formula2:
            tag(doc, 'formula2', body=data_validation.formula2)
        end_tag(doc, 'dataValidation')
    end_tag(doc, 'dataValidations')

def write_worksheet_hyperlinks(doc, worksheet):
    """Write worksheet hyperlinks to xml."""
    write_hyperlinks = False
    for cell in worksheet.get_cell_collection():
        if cell.hyperlink_rel_id is not None:
            write_hyperlinks = True
            break
    if write_hyperlinks:
        start_tag(doc, 'hyperlinks')
        for cell in worksheet.get_cell_collection():
            if cell.hyperlink_rel_id is not None:
                attrs = {'display': cell.hyperlink,
                        'ref': cell.get_coordinate(),
                        'r:id': cell.hyperlink_rel_id}
                tag(doc, 'hyperlink', attrs)
        end_tag(doc, 'hyperlinks')


def write_worksheet_rels(worksheet, idx):
    """Write relationships for the worksheet to xml."""
    root = Element('Relationships', {'xmlns': 'http://schemas.openxmlformats.org/package/2006/relationships'})
    for rel in worksheet.relationships:
        attrs = {'Id': rel.id, 'Type': rel.type, 'Target': rel.target}
        if rel.target_mode:
            attrs['TargetMode'] = rel.target_mode
        SubElement(root, 'Relationship', attrs)
    if worksheet._charts or worksheet._images:
        attrs = {'Id' : 'rId1',
            'Type' : 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing',
            'Target' : '../drawings/drawing%s.xml' % idx }
        SubElement(root, 'Relationship', attrs)
    return get_document_content(root)
