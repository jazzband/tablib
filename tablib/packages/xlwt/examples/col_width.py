#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman
__rev_id__ = """$Id: col_width.py 3315 2008-03-14 14:44:52Z chris $"""


from xlwt import *

w = Workbook()
ws = w.add_sheet('Hey, Dude')

for i in range(6, 80):
    fnt = Font()
    fnt.height = i*20
    style = XFStyle()
    style.font = fnt
    ws.write(1, i, 'Test')
    ws.col(i).width = 0x0d00 + i
w.save('col_width.xls')
