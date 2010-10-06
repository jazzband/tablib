#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

wb = Workbook()
ws0 = wb.add_sheet('sheet0')


fnt = Font()
fnt.name = 'Arial'
fnt.colour_index = 4
fnt.bold = True

borders = Borders()
borders.left = 6
borders.right = 6
borders.top = 6
borders.bottom = 6

style = XFStyle()
style.font = fnt
style.borders = borders

ws0.write_merge(3, 3, 1, 5, 'test1', style)
ws0.write_merge(4, 10, 1, 5, 'test2', style)
ws0.col(1).width = 0x0d00

wb.save('merged0.xls')
