# file openpyxl/writer/styles.py

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

"""Write the shared style table."""

# package imports
from ..shared.xmltools import Element, SubElement
from ..shared.xmltools import get_document_content
from .. import style

class StyleWriter(object):

    def __init__(self, workbook):
        self._style_list = self._get_style_list(workbook)
        self._root = Element('styleSheet',
            {'xmlns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'})

    def _get_style_list(self, workbook):
        crc = {}
        for worksheet in workbook.worksheets:
            for style in worksheet._styles.values():
                crc[hash(style)] = style
        self.style_table = dict([(style, i+1) \
            for i, style in enumerate(crc.values())])
        sorted_styles = sorted(self.style_table.items(), \
            key = lambda pair:pair[1])
        return [s[0] for s in sorted_styles]

    def get_style_by_hash(self):
        return dict([(hash(style), id) \
            for style, id in self.style_table.items()])

    def write_table(self):
        number_format_table = self._write_number_formats()
        fonts_table = self._write_fonts()
        fills_table = self._write_fills()
        borders_table = self._write_borders()
        self._write_cell_style_xfs()
        self._write_cell_xfs(number_format_table, fonts_table, fills_table, borders_table)
        self._write_cell_style()
        self._write_dxfs()
        self._write_table_styles()

        return get_document_content(xml_node=self._root)

    def _write_fonts(self):
        """ add fonts part to root
            return {font.crc => index}
        """

        fonts = SubElement(self._root, 'fonts')

        # default
        font_node = SubElement(fonts, 'font')
        SubElement(font_node, 'sz', {'val':'11'})
        SubElement(font_node, 'color', {'theme':'1'})
        SubElement(font_node, 'name', {'val':'Calibri'})
        SubElement(font_node, 'family', {'val':'2'})
        SubElement(font_node, 'scheme', {'val':'minor'})

        # others
        table = {}
        index = 1
        for st in self._style_list:
            if hash(st.font) != hash(style.DEFAULTS.font) and hash(st.font) not in table:
                table[hash(st.font)] = str(index)
                font_node = SubElement(fonts, 'font')
                SubElement(font_node, 'sz', {'val':str(st.font.size)})
                SubElement(font_node, 'color', {'rgb':str(st.font.color.index)})
                SubElement(font_node, 'name', {'val':st.font.name})
                SubElement(font_node, 'family', {'val':'2'})
                SubElement(font_node, 'scheme', {'val':'minor'})
                if st.font.bold:
                    SubElement(font_node, 'b')
                if st.font.italic:
                    SubElement(font_node, 'i')
                index += 1

        fonts.attrib["count"] = str(index)
        return table

    def _write_fills(self):
        fills = SubElement(self._root, 'fills', {'count':'2'})
        fill = SubElement(fills, 'fill')
        SubElement(fill, 'patternFill', {'patternType':'none'})
        fill = SubElement(fills, 'fill')
        SubElement(fill, 'patternFill', {'patternType':'gray125'})

        table = {}
        index = 2
        for st in self._style_list:
            if hash(st.fill) != hash(style.DEFAULTS.fill) and hash(st.fill) not in table:
                table[hash(st.fill)] = str(index)
                fill = SubElement(fills, 'fill')
                if hash(st.fill.fill_type) != hash(style.DEFAULTS.fill.fill_type):
                    node = SubElement(fill,'patternFill', {'patternType':st.fill.fill_type})
                    if hash(st.fill.start_color) != hash(style.DEFAULTS.fill.start_color):

                        SubElement(node, 'fgColor', {'rgb':str(st.fill.start_color.index)})
                    if hash(st.fill.end_color) != hash(style.DEFAULTS.fill.end_color):
                        SubElement(node, 'bgColor', {'rgb':str(st.fill.start_color.index)})
                index += 1

        fills.attrib["count"] = str(index)
        return table

    def _write_borders(self):
        borders = SubElement(self._root, 'borders')

        # default
        border = SubElement(borders, 'border')
        SubElement(border, 'left')
        SubElement(border, 'right')
        SubElement(border, 'top')
        SubElement(border, 'bottom')
        SubElement(border, 'diagonal')

        # others
        table = {}
        index = 1
        for st in self._style_list:
            if hash(st.borders) != hash(style.DEFAULTS.borders) and hash(st.borders) not in table:
                table[hash(st.borders)] = str(index)
                border = SubElement(borders, 'border')
                # caution: respect this order
                for side in ('left','right','top','bottom','diagonal'):
                    obj = getattr(st.borders, side)
                    node = SubElement(border, side, {'style':obj.border_style})
                    SubElement(node, 'color', {'rgb':str(obj.color.index)})
                index += 1

        borders.attrib["count"] = str(index)
        return table

    def _write_cell_style_xfs(self):
        cell_style_xfs = SubElement(self._root, 'cellStyleXfs', {'count':'1'})
        xf = SubElement(cell_style_xfs, 'xf',
            {'numFmtId':"0", 'fontId':"0", 'fillId':"0", 'borderId':"0"})

    def _write_cell_xfs(self, number_format_table, fonts_table, fills_table, borders_table):
        """ write styles combinations based on ids found in tables """

        # writing the cellXfs
        cell_xfs = SubElement(self._root, 'cellXfs',
            {'count':'%d' % (len(self._style_list) + 1)})

        # default
        def _get_default_vals():
            return dict(numFmtId='0', fontId='0', fillId='0',
                xfId='0', borderId='0')

        SubElement(cell_xfs, 'xf', _get_default_vals())

        for st in self._style_list:
            vals = _get_default_vals()

            if hash(st.font) != hash(style.DEFAULTS.font):
                vals['fontId'] = fonts_table[hash(st.font)]
                vals['applyFont'] = '1'

            if hash(st.borders) != hash(style.DEFAULTS.borders):
                vals['borderId'] = borders_table[hash(st.borders)]
                vals['applyBorder'] = '1'

            if hash(st.fill) != hash(style.DEFAULTS.fill):
                vals['fillId'] = fills_table[hash(st.fill)]
                vals['applyFillId'] = '1'

            if st.number_format != style.DEFAULTS.number_format:
                vals['numFmtId'] = '%d' % number_format_table[st.number_format]
                vals['applyNumberFormat'] = '1'

            if hash(st.alignment) != hash(style.DEFAULTS.alignment):
                vals['applyAlignment'] = '1'

            node = SubElement(cell_xfs, 'xf', vals)

            if hash(st.alignment) != hash(style.DEFAULTS.alignment):
                alignments = {}

                for align_attr in ['horizontal','vertical']:
                    if hash(getattr(st.alignment, align_attr)) != hash(getattr(style.DEFAULTS.alignment, align_attr)):
                        alignments[align_attr] = getattr(st.alignment, align_attr)

                SubElement(node, 'alignment', alignments)


    def _write_cell_style(self):
        cell_styles = SubElement(self._root, 'cellStyles', {'count':'1'})
        cell_style = SubElement(cell_styles, 'cellStyle',
            {'name':"Normal", 'xfId':"0", 'builtinId':"0"})

    def _write_dxfs(self):
        dxfs = SubElement(self._root, 'dxfs', {'count':'0'})

    def _write_table_styles(self):

        table_styles = SubElement(self._root, 'tableStyles',
            {'count':'0', 'defaultTableStyle':'TableStyleMedium9',
            'defaultPivotStyle':'PivotStyleLight16'})

    def _write_number_formats(self):

        number_format_table = {}

        number_format_list = []
        exceptions_list = []
        num_fmt_id = 165 # start at a greatly higher value as any builtin can go
        num_fmt_offset = 0

        for style in self._style_list:

            if not style.number_format in number_format_list  :
                number_format_list.append(style.number_format)

        for number_format in number_format_list:

            if number_format.is_builtin():
                btin = number_format.builtin_format_id(number_format.format_code)
                number_format_table[number_format] = btin
            else:
                number_format_table[number_format] = num_fmt_id + num_fmt_offset
                num_fmt_offset += 1
                exceptions_list.append(number_format)

        num_fmts = SubElement(self._root, 'numFmts',
            {'count':'%d' % len(exceptions_list)})

        for number_format in exceptions_list :
            SubElement(num_fmts, 'numFmt',
                {'numFmtId':'%d' % number_format_table[number_format],
                'formatCode':'%s' % number_format.format_code})

        return number_format_table
