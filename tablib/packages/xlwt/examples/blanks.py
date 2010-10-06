#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

font0 = Font()
font0.name = 'Times New Roman'
font0.struck_out = True
font0.bold = True

style0 = XFStyle()
style0.font = font0


wb = Workbook()
ws0 = wb.add_sheet('0')

ws0.write(1, 1, 'Test', style0)

for i in range(0, 0x53):
    borders = Borders()
    borders.left = i
    borders.right = i
    borders.top = i
    borders.bottom = i

    style = XFStyle()
    style.borders = borders

    ws0.write(i, 2, '', style)
    ws0.write(i, 3, hex(i), style0)

ws0.write_merge(5, 8, 6, 10, "")

wb.save('blanks.xls')
