#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

f = Font()
f.height = 20*72
f.name = 'Verdana'
f.bold = True
f.underline = Font.UNDERLINE_DOUBLE
f.colour_index = 4

h_style = XFStyle()
h_style.font = f

w = Workbook()
ws = w.add_sheet('F')

##############
## NOTE: parameters are separated by semicolon!!!
##############

n = "HYPERLINK"
ws.write_merge(1, 1, 1, 10, Formula(n + '("http://www.irs.gov/pub/irs-pdf/f1000.pdf";"f1000.pdf")'), h_style)
ws.write_merge(2, 2, 2, 25, Formula(n + '("mailto:roman.kiseliov@gmail.com?subject=pyExcelerator-feedback&Body=Hello,%20Roman!";"pyExcelerator-feedback")'), h_style)

w.save("hyperlinks.xls")
