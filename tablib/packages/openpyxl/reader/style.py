# file openpyxl/reader/style.py

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

"""Read shared style definitions"""

# package imports
from ..shared.xmltools import fromstring, QName
from ..shared.exc import MissingNumberFormat
from ..style import Style, NumberFormat


def read_style_table(xml_source):
    """Read styles from the shared style table"""
    table = {}
    xmlns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    root = fromstring(xml_source)
    custom_num_formats = parse_custom_num_formats(root, xmlns)
    builtin_formats = NumberFormat._BUILTIN_FORMATS
    cell_xfs = root.find(QName(xmlns, 'cellXfs').text)
    cell_xfs_nodes = cell_xfs.findall(QName(xmlns, 'xf').text)
    for index, cell_xfs_node in enumerate(cell_xfs_nodes):
        new_style = Style()
        number_format_id = int(cell_xfs_node.get('numFmtId'))
        if number_format_id < 164:
            new_style.number_format.format_code = \
                    builtin_formats.get(number_format_id, 'General')
        else:

            if number_format_id in custom_num_formats:
                new_style.number_format.format_code = \
                        custom_num_formats[number_format_id]
            else:
                raise MissingNumberFormat('%s' % number_format_id)
        table[index] = new_style
    return table


def parse_custom_num_formats(root, xmlns):
    """Read in custom numeric formatting rules from the shared style table"""
    custom_formats = {}
    num_fmts = root.find(QName(xmlns, 'numFmts').text)
    if num_fmts is not None:
        num_fmt_nodes = num_fmts.findall(QName(xmlns, 'numFmt').text)
        for num_fmt_node in num_fmt_nodes:
            custom_formats[int(num_fmt_node.get('numFmtId'))] = \
                    num_fmt_node.get('formatCode')
    return custom_formats
