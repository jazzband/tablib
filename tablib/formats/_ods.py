# -*- coding: utf-8 -*-

""" Tablib - ODF Support.
"""

import sys
import re
import tablib

if sys.version_info[0] > 2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from tablib.compat import opendocument, style, table, text, unicode

title = 'ods'
extensions = ('ods',)

bold = style.Style(name="bold", family="paragraph")
bold.addElement(style.TextProperties(fontweight="bold", fontweightasian="bold", fontweightcomplex="bold"))


def detect(stream):
    """Returns True if given stream is a readable excel file."""
    try:
        opendocument.load(BytesIO(stream))
        return True
    except:
        pass


def export_set(dataset):
    """Returns ODF representation of Dataset."""

    wb = opendocument.OpenDocumentSpreadsheet()
    wb.automaticstyles.addElement(bold)

    ws = table.Table(name=dataset.title if dataset.title else 'Tablib Dataset')
    wb.spreadsheet.addElement(ws)
    dset_sheet(dataset, ws)

    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def export_book(databook):
    """Returns ODF representation of DataBook."""

    wb = opendocument.OpenDocumentSpreadsheet()
    wb.automaticstyles.addElement(bold)

    for i, dset in enumerate(databook._datasets):
        ws = table.Table(name=dset.title if dset.title else 'Sheet%s' % (i))
        wb.spreadsheet.addElement(ws)
        dset_sheet(dset, ws)


    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


class ODSReader():
    # Copyright 2011 Marco Conti

    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at

    #   http://www.apache.org/licenses/LICENSE-2.0

    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.

    # Thanks to grt for the fixes

    # loads the file
    def __init__(self, file):
        self.doc = opendocument.load(file)
        self.SHEETS = {}
        for sheet in self.doc.spreadsheet.getElementsByType(table.Table):
            self.readSheet(sheet)

    # reads a sheet in the sheet dictionary, storing each sheet as an array
    # (rows) of arrays (columns)
    def readSheet(self, sheet):
        name = sheet.getAttribute("name")
        rows = sheet.getElementsByType(table.TableRow)
        arrRows = []
        # get longestRow to not fill empty rows with blanks, shortens runtime
        cols = sheet.getElementsByType(table.TableColumn)
        try:
            longestRow = int(max([col.getAttribute("numbercolumnsrepeated") for col in cols]))
        except:
            longestRow = 0
        # for each row
        for row in rows:
            row_comment = ""
            arrCells = []
            cells = row.getElementsByType(table.TableCell)

            # for each cell
            for cell in cells:
                # repeated value?
                repeat = cell.getAttribute("numbercolumnsrepeated")
                if(not repeat):
                    repeat = 1

                ps = cell.getElementsByType(text.P)
                textContent = ""

                # for each text node
                for p in ps:
                    for n in p.childNodes:
                        if (n.nodeType == 3):
                            textContent = textContent + unicode(n.data)

                if(textContent):
                    if(textContent[0] != "#"):  # ignore comments cells
                        for rr in range(int(repeat)):  # repeated?
                            arrCells.append(textContent)

                    else:
                        row_comment = row_comment + textContent + " "
                else:
                    if int(repeat) < longestRow:
                        for rr in range(int(repeat)):  # repeated?
                            arrCells.append('')  # for empty cells
                    else:
                        arrCells.append('')

            # if row contained something
            if(len(arrCells)):
                arrRows.append(arrCells)

            # else:
            #   print "Empty or commented row (", row_comment, ")"

        self.SHEETS[name] = arrRows

    # returns a sheet as an array (rows) of arrays (columns)
    def getSheet(self, name):
        return self.SHEETS[name]


def import_set(dset, in_stream, headers=True):
    """Returns databook from ODS stream."""
    dset.wipe()
    od = ODSReader(BytesIO(in_stream))  # returns dict with sheetnames as keys
    sheet = sorted(od.SHEETS.iterkeys())[0]
    dset.title = sheet
    datals = []  # save in regular list first, ODSReader doesnt fill with blanks
    for row in od.getSheet(sheet):
        datals.append(row)
    try:
        longest = max([len(x) for x in od.getSheet(sheet)])
    except ValueError:
        longest = 0
    for i, item in enumerate(datals):
        if len(item) < longest:
            for i in range(longest - len(item)):
                item.append('')  # rows get all the same length
        if (row == 0) and (headers):
            dset.headers = item
        else:
            dset.append(item)


def import_book(dbook, in_stream, headers=True):
    """Returns databook from ODS stream."""
    dbook.wipe()
    od = ODSReader(BytesIO(in_stream))  # returns dict with sheetnames as keys
    for sheet in sorted(od.SHEETS.iterkeys()):
        dset = tablib.Dataset()
        datals = []  # save in regular list first, ODSReader doesnt fill with blanks
        dset.title = sheet
        for row in od.getSheet(sheet):
            datals.append(row)
        try:
            longest = max([len(x) for x in od.getSheet(sheet)])
        except ValueError:
            longest = 0
        for i, item in enumerate(datals):
            if len(item) < longest:
                for i in range(longest - len(item)):
                    item.append('')  # rows get all the same length
            if (row == 0) and (headers):
                dset.headers = item
            else:
                dset.append(item)
        dbook.add_sheet(dset)


def dset_sheet(dataset, ws):
    """Completes given worksheet from given Dataset."""
    def float_or_not(val):  # float output
        fltExp = re.compile('^\s*[-+]?\d+(\.\d+)?\s*$')
        if fltExp.match(str(val)):
            tc = table.TableCell(valuetype="float", value=str(val).strip())
        else:
            tc = table.TableCell(valuetype="string")
        return tc

    _package = dataset._package(dicts=False)

    for i, sep in enumerate(dataset._separators):
        _offset = i
        _package.insert((sep[0] + _offset), (sep[1],))

    for i, row in enumerate(_package):
        row_number = i + 1
        odf_row = table.TableRow(stylename=bold, defaultcellstylename='bold')
        for j, col in enumerate(row):
            try:
                col = unicode(col, errors='ignore')
            except TypeError:
                ## col is already unicode
                pass
            ws.addElement(table.TableColumn())

            # bold headers
            if (row_number == 1) and dataset.headers:
                odf_row.setAttribute('stylename', bold)
                ws.addElement(odf_row)
                cell = float_or_not(col)
                p = text.P()
                p.addElement(text.Span(text=col, stylename=bold))
                cell.addElement(p)
                odf_row.addElement(cell)

            # wrap the rest
            else:
                try:
                    if '\n' in col:
                        ws.addElement(odf_row)
                        cell = float_or_not(col)
                        cell.addElement(text.P(text=col))
                        odf_row.addElement(cell)
                    else:
                        ws.addElement(odf_row)
                        cell = float_or_not(col)
                        cell.addElement(text.P(text=col))
                        odf_row.addElement(cell)
                except TypeError:
                    ws.addElement(odf_row)
                    cell = float_or_not(col)
                    cell.addElement(text.P(text=col))
                    odf_row.addElement(cell)