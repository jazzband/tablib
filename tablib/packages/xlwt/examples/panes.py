#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

w = Workbook()
ws1 = w.add_sheet('sheet 1')
ws2 = w.add_sheet('sheet 2')
ws3 = w.add_sheet('sheet 3')
ws4 = w.add_sheet('sheet 4')
ws5 = w.add_sheet('sheet 5')
ws6 = w.add_sheet('sheet 6')

for i in range(0x100):
    ws1.write(i/0x10, i%0x10, i)

for i in range(0x100):
    ws2.write(i/0x10, i%0x10, i)

for i in range(0x100):
    ws3.write(i/0x10, i%0x10, i)

for i in range(0x100):
    ws4.write(i/0x10, i%0x10, i)

for i in range(0x100):
    ws5.write(i/0x10, i%0x10, i)

for i in range(0x100):
    ws6.write(i/0x10, i%0x10, i)

ws1.panes_frozen = True
ws1.horz_split_pos = 2

ws2.panes_frozen = True
ws2.vert_split_pos = 2

ws3.panes_frozen = True
ws3.horz_split_pos = 1
ws3.vert_split_pos = 1

ws4.panes_frozen = False
ws4.horz_split_pos = 12
ws4.horz_split_first_visible = 2

ws5.panes_frozen = False
ws5.vert_split_pos = 40
ws4.vert_split_first_visible = 2

ws6.panes_frozen = False
ws6.horz_split_pos = 12
ws4.horz_split_first_visible = 2
ws6.vert_split_pos = 40
ws4.vert_split_first_visible = 2

w.save('panes.xls')

