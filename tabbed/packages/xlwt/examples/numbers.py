#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

w = Workbook()
ws = w.add_sheet('Hey, Dude')

ws.write(0, 0, 1)
ws.write(1, 0, 1.23)
ws.write(2, 0, 12345678)
ws.write(3, 0, 123456.78)

ws.write(0, 1, -1)
ws.write(1, 1, -1.23)
ws.write(2, 1, -12345678)
ws.write(3, 1, -123456.78)

ws.write(0, 2, -17867868678687.0)
ws.write(1, 2, -1.23e-5)
ws.write(2, 2, -12345678.90780980)
ws.write(3, 2, -123456.78)

w.save('numbers.xls')
