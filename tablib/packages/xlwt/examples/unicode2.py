#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

w = Workbook()
ws1 = w.add_sheet(u'\N{GREEK SMALL LETTER ALPHA}\N{GREEK SMALL LETTER BETA}\N{GREEK SMALL LETTER GAMMA}\u2665\u041e\u041b\u042f\u2665')

fnt = Font()
fnt.height = 26*20
style = XFStyle()
style.font = fnt

for i in range(0x10000):
    ws1.write(i/0x10, i%0x10, unichr(i), style)

w.save('unicode2.xls')

