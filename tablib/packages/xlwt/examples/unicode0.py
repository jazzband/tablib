#!/usr/bin/env python
import xlwt

# Strings passed to (for example) Worksheet.write can be unicode objects,
# or str (8-bit) objects, which are then decoded into unicode.
# The encoding to be used defaults to 'ascii'. This can be overridden
# when the Workbook instance is created:

book = xlwt.Workbook(encoding='cp1251')
sheet = book.add_sheet('cp1251-demo')
sheet.write(0, 0, '\xce\xeb\xff')
book.save('unicode0.xls')
