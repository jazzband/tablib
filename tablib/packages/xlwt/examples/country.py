#!/usr/bin/env python
# -*- coding: windows-1252 -*-
# Copyright (C) 2007 John Machin

from xlwt import *

w = Workbook()
w.country_code = 61
ws = w.add_sheet('AU')
w.save('country.xls')
