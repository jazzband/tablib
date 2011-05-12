# file openpyxl/writer/workbook.py

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

"""Write the workbook global settings to the archive."""

# package imports
from ..shared.xmltools import Element, SubElement
from ..cell import absolute_coordinate
from ..shared.xmltools import get_document_content
from ..shared.ooxml import NAMESPACES, ARC_CORE, ARC_WORKBOOK, \
       ARC_APP, ARC_THEME, ARC_STYLE, ARC_SHARED_STRINGS
from ..shared.date_time import datetime_to_W3CDTF


def write_properties_core(properties):
    """Write the core properties to xml."""
    root = Element('cp:coreProperties', {'xmlns:cp': NAMESPACES['cp'],
            'xmlns:xsi': NAMESPACES['xsi'], 'xmlns:dc': NAMESPACES['dc'],
            'xmlns:dcterms': NAMESPACES['dcterms'],
            'xmlns:dcmitype': NAMESPACES['dcmitype'], })
    SubElement(root, 'dc:creator').text = properties.creator
    SubElement(root, 'cp:lastModifiedBy').text = properties.last_modified_by
    SubElement(root, 'dcterms:created', \
            {'xsi:type': 'dcterms:W3CDTF'}).text = \
            datetime_to_W3CDTF(properties.created)
    SubElement(root, 'dcterms:modified',
            {'xsi:type': 'dcterms:W3CDTF'}).text = \
            datetime_to_W3CDTF(properties.modified)
    return get_document_content(root)


def write_content_types(workbook):
    """Write the content-types xml."""
    root = Element('Types', {'xmlns': 'http://schemas.openxmlformats.org/package/2006/content-types'})
    SubElement(root, 'Override', {'PartName': '/' + ARC_THEME, 'ContentType': 'application/vnd.openxmlformats-officedocument.theme+xml'})
    SubElement(root, 'Override', {'PartName': '/' + ARC_STYLE, 'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml'})
    SubElement(root, 'Default', {'Extension': 'rels', 'ContentType': 'application/vnd.openxmlformats-package.relationships+xml'})
    SubElement(root, 'Default', {'Extension': 'xml', 'ContentType': 'application/xml'})
    SubElement(root, 'Override', {'PartName': '/' + ARC_WORKBOOK, 'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml'})
    SubElement(root, 'Override', {'PartName': '/' + ARC_APP, 'ContentType': 'application/vnd.openxmlformats-officedocument.extended-properties+xml'})
    SubElement(root, 'Override', {'PartName': '/' + ARC_CORE, 'ContentType': 'application/vnd.openxmlformats-package.core-properties+xml'})
    SubElement(root, 'Override', {'PartName': '/' + ARC_SHARED_STRINGS, 'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml'})

    drawing_id = 1
    chart_id = 1

    for sheet_id, sheet in enumerate(workbook.worksheets):
        SubElement(root, 'Override',
                {'PartName': '/xl/worksheets/sheet%d.xml' % (sheet_id + 1),
                'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml'})
        if sheet._charts:
            SubElement(root, 'Override',
                {'PartName' : '/xl/drawings/drawing%d.xml' % (sheet_id + 1),
                'ContentType' : 'application/vnd.openxmlformats-officedocument.drawing+xml'})
            drawing_id += 1

            for chart in sheet._charts:
                SubElement(root, 'Override',
                    {'PartName' : '/xl/charts/chart%d.xml' % chart_id,
                    'ContentType' : 'application/vnd.openxmlformats-officedocument.drawingml.chart+xml'})
                chart_id += 1
                if chart._shapes:
                    SubElement(root, 'Override',
                        {'PartName' : '/xl/drawings/drawing%d.xml' % drawing_id,
                        'ContentType' : 'application/vnd.openxmlformats-officedocument.drawingml.chartshapes+xml'})
                    drawing_id += 1

    return get_document_content(root)


def write_properties_app(workbook):
    """Write the properties xml."""
    worksheets_count = len(workbook.worksheets)
    root = Element('Properties', {'xmlns': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
            'xmlns:vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'})
    SubElement(root, 'Application').text = 'Microsoft Excel'
    SubElement(root, 'DocSecurity').text = '0'
    SubElement(root, 'ScaleCrop').text = 'false'
    SubElement(root, 'Company')
    SubElement(root, 'LinksUpToDate').text = 'false'
    SubElement(root, 'SharedDoc').text = 'false'
    SubElement(root, 'HyperlinksChanged').text = 'false'
    SubElement(root, 'AppVersion').text = '12.0000'

    # heading pairs part
    heading_pairs = SubElement(root, 'HeadingPairs')
    vector = SubElement(heading_pairs, 'vt:vector',
            {'size': '2', 'baseType': 'variant'})
    variant = SubElement(vector, 'vt:variant')
    SubElement(variant, 'vt:lpstr').text = 'Worksheets'
    variant = SubElement(vector, 'vt:variant')
    SubElement(variant, 'vt:i4').text = '%d' % worksheets_count

    # title of parts
    title_of_parts = SubElement(root, 'TitlesOfParts')
    vector = SubElement(title_of_parts, 'vt:vector',
            {'size': '%d' % worksheets_count, 'baseType': 'lpstr'})
    for ws in workbook.worksheets:
        SubElement(vector, 'vt:lpstr').text = '%s' % ws.title
    return get_document_content(root)


def write_root_rels(workbook):
    """Write the relationships xml."""
    root = Element('Relationships', {'xmlns':
            'http://schemas.openxmlformats.org/package/2006/relationships'})
    SubElement(root, 'Relationship', {'Id': 'rId1', 'Target': ARC_WORKBOOK,
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument'})
    SubElement(root, 'Relationship', {'Id': 'rId2', 'Target': ARC_CORE,
            'Type': 'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties'})
    SubElement(root, 'Relationship', {'Id': 'rId3', 'Target': ARC_APP,
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties'})
    return get_document_content(root)


def write_workbook(workbook):
    """Write the core workbook xml."""
    root = Element('workbook', {'xmlns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'xml:space': 'preserve', 'xmlns:r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'})
    SubElement(root, 'fileVersion', {'appName': 'xl', 'lastEdited': '4',
            'lowestEdited': '4', 'rupBuild': '4505'})
    SubElement(root, 'workbookPr', {'defaultThemeVersion': '124226',
            'codeName': 'ThisWorkbook'})
    book_views = SubElement(root, 'bookViews')
    SubElement(book_views, 'workbookView', {'activeTab': '%d' % workbook.get_index(workbook.get_active_sheet()),
            'autoFilterDateGrouping': '1', 'firstSheet': '0', 'minimized': '0',
            'showHorizontalScroll': '1', 'showSheetTabs': '1',
            'showVerticalScroll': '1', 'tabRatio': '600',
            'visibility': 'visible'})
    # worksheets
    sheets = SubElement(root, 'sheets')
    for i, sheet in enumerate(workbook.worksheets):
        sheet_node = SubElement(sheets, 'sheet', {'name': sheet.title,
                'sheetId': '%d' % (i + 1), 'r:id': 'rId%d' % (i + 1)})
        if not sheet.sheet_state == sheet.SHEETSTATE_VISIBLE:
            sheet_node.set('state', sheet.sheet_state)
    # named ranges
    defined_names = SubElement(root, 'definedNames')
    for named_range in workbook.get_named_ranges():
        name = SubElement(defined_names, 'definedName',
                {'name': named_range.name})

        # as there can be many cells in one range, generate the list of ranges
        dest_cells = []
        cell_ids = []
        for worksheet, range_name in named_range.destinations:
            cell_ids.append(workbook.get_index(worksheet))
            dest_cells.append("'%s'!%s" % (worksheet.title.replace("'", "''"),
                                           absolute_coordinate(range_name)))

        # for local ranges, we must check all the cells belong to the same sheet
        base_id = cell_ids[0]
        if named_range.local_only and all([x == base_id for x in cell_ids]):
            name.set('localSheetId', '%s' % base_id)

        # finally write the cells list
        name.text = ','.join(dest_cells)

    SubElement(root, 'calcPr', {'calcId': '124519', 'calcMode': 'auto',
            'fullCalcOnLoad': '1'})
    return get_document_content(root)


def write_workbook_rels(workbook):
    """Write the workbook relationships xml."""
    root = Element('Relationships', {'xmlns':
            'http://schemas.openxmlformats.org/package/2006/relationships'})
    for i in range(len(workbook.worksheets)):
        SubElement(root, 'Relationship', {'Id': 'rId%d' % (i + 1),
                'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet',
                'Target': 'worksheets/sheet%s.xml' % (i + 1)})
    rid = len(workbook.worksheets) + 1
    SubElement(root, 'Relationship',
            {'Id': 'rId%d' % rid, 'Target': 'sharedStrings.xml',
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings'})
    SubElement(root, 'Relationship',
            {'Id': 'rId%d' % (rid + 1), 'Target': 'styles.xml',
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles'})
    SubElement(root, 'Relationship',
            {'Id': 'rId%d' % (rid + 2), 'Target': 'theme/theme1.xml',
            'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme'})
    return get_document_content(root)
