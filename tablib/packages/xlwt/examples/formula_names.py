#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *
from xlwt.ExcelFormulaParser import FormulaParseException

w = Workbook()
ws = w.add_sheet('F')

## This example is a little silly since the formula building is
## so simplistic that it often fails because the generated text
## has the wrong number of parameters for the function being
## tested.

i = 0
succeed_count = 0
fail_count = 0
for n in sorted(ExcelMagic.std_func_by_name):
    ws.write(i, 0, n)
    text = n + "($A$1)"
    try:
        formula = Formula(text)
    except FormulaParseException,e:
        print "Could not parse %r: %s" % (text,e.args[0])
        fail_count += 1
    else:
        ws.write(i, 3, formula)
        succeed_count += 1
    i += 1

w.save('formula_names.xls')

print "succeeded with %i functions, failed with %i" % (succeed_count,fail_count)
