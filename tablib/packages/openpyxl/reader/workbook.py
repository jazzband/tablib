# file openpyxl/reader/workbook.py

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

"""Read in global settings to be maintained by the workbook object."""

# package imports
from openpyxl.shared.xmltools import fromstring, QName
from openpyxl.shared.ooxml import NAMESPACES
from openpyxl.workbook import DocumentProperties
from openpyxl.shared.date_time import W3CDTF_to_datetime,CALENDAR_WINDOWS_1900,CALENDAR_MAC_1904
from openpyxl.namedrange import NamedRange, NamedRangeContainingValue, split_named_range, refers_to_range

import datetime

# constants
BUGGY_NAMED_RANGES = ['NA()', '#REF!']
DISCARDED_RANGES = ['Excel_BuiltIn', 'Print_Area']

def get_sheet_ids(xml_source):

    sheet_names = read_sheets_titles(xml_source)

    return dict((sheet, 'sheet%d.xml' % (i + 1)) for i, sheet in enumerate(sheet_names))


def read_properties_core(xml_source):
    """Read assorted file properties."""
    properties = DocumentProperties()
    root = fromstring(xml_source)
    creator_node = root.find(QName(NAMESPACES['dc'], 'creator').text)
    if creator_node is not None:
        properties.creator = creator_node.text
    else:
        properties.creator = ''
    last_modified_by_node = root.find(
            QName(NAMESPACES['cp'], 'lastModifiedBy').text)
    if last_modified_by_node is not None:
        properties.last_modified_by = last_modified_by_node.text
    else:
        properties.last_modified_by = ''

    created_node = root.find(QName(NAMESPACES['dcterms'], 'created').text)
    if created_node is not None:
        properties.created = W3CDTF_to_datetime(created_node.text)
    else:
        properties.created = datetime.datetime.now()

    modified_node = root.find(QName(NAMESPACES['dcterms'], 'modified').text)
    if modified_node is not None:
        properties.modified = W3CDTF_to_datetime(modified_node.text)
    else:
        properties.modified = properties.created

    return properties


def read_excel_base_date(xml_source):
    root = fromstring(text = xml_source)
    wbPr = root.find(QName('http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'workbookPr').text)
    if ('date1904' in wbPr.keys() and wbPr.attrib['date1904'] in ('1', 'true')):
        return CALENDAR_MAC_1904

    return CALENDAR_WINDOWS_1900


def read_sheets_titles(xml_source):
    """Read titles for all sheets."""
    root = fromstring(xml_source)
    titles_root = root.find(QName('http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'sheets').text)

    return [sheet.get('name') for sheet in titles_root.getchildren()]

def read_named_ranges(xml_source, workbook):
    """Read named ranges, excluding poorly defined ranges."""
    named_ranges = []
    root = fromstring(xml_source)
    names_root = root.find(QName('http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'definedNames').text)
    if names_root is not None:

        for name_node in names_root.getchildren():
            range_name = name_node.get('name')

            if name_node.get("hidden", '0') == '1':
                continue

            valid = True

            for discarded_range in DISCARDED_RANGES:
                if discarded_range in range_name:
                    valid = False

            for bad_range in BUGGY_NAMED_RANGES:
                if bad_range in name_node.text:
                    valid = False

            if valid:
                if refers_to_range(name_node.text):
                    destinations = split_named_range(name_node.text)

                    new_destinations = []
                    for worksheet, cells_range in destinations:
                        # it can happen that a valid named range references
                        # a missing worksheet, when Excel didn't properly maintain
                        # the named range list
                        #
                        # we just ignore them here
                        worksheet = workbook.get_sheet_by_name(worksheet)
                        if worksheet:
                            new_destinations.append((worksheet, cells_range))

                    named_range = NamedRange(range_name, new_destinations)
                else:
                    named_range = NamedRangeContainingValue(range_name, name_node.text)

                location_id = name_node.get("localSheetId")
                if location_id:
                    named_range.scope = workbook.worksheets[int(location_id)]

                named_ranges.append(named_range)

    return named_ranges
