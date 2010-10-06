#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

fnt = Font()
fnt.name = 'Arial'
fnt.colour_index = 4
fnt.bold = True

borders = Borders()
borders.left = 6
borders.right = 6
borders.top = 6
borders.bottom = 6

al = Alignment()
al.horz = Alignment.HORZ_CENTER
al.vert = Alignment.VERT_CENTER

style = XFStyle()
style.font = fnt
style.borders = borders
style.alignment = al


wb = Workbook()
ws0 = wb.add_sheet('sheet0')
ws1 = wb.add_sheet('sheet1')
ws2 = wb.add_sheet('sheet2')

for i in range(0, 0x200, 2):
    ws0.write_merge(i, i+1, 1, 5, 'test %d' % i, style)
    ws1.write_merge(i, i, 1, 7, 'test %d' % i, style)
    ws2.write_merge(i, i+1, 1, 7 + (i%10), 'test %d' % i, style)


wb.save('merged.xls')
