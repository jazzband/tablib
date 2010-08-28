#!/usr/bin/env python
# -*- coding: ascii -*-
# Portions Copyright (C) 2005 Kiseliov Roman

import xlwt

style = xlwt.easyxf(
    "font: name Arial, colour_index blue, bold on;"
    "borders: top double, bottom double, left double, right double;"
    )

def write_data_cells(ws):
    ws.write_merge(1, 1, 1, 5, 'test 1', style)
    ws.write_merge(2, 2, 1, 4, 'test 1', style)
    ws.write_merge(3, 3, 1, 3, 'test 2', style)
    ws.write_merge(4, 4, 1, 4, 'test 1', style)
    ws.write_merge(5, 5, 1, 4, 'test 3', style)
    ws.write_merge(6, 6, 1, 5, 'test 1', style)
    ws.write_merge(7, 7, 1, 5, 'test 4', style)
    ws.write_merge(8, 8, 1, 4, 'test 1', style)
    ws.write_merge(9, 9, 1, 3, 'test 5', style)

def write_row_outline_levels(ws):
    ws.row(1).level = 1
    ws.row(2).level = 1
    ws.row(3).level = 2
    ws.row(4).level = 2
    ws.row(5).level = 2
    ws.row(6).level = 2
    ws.row(7).level = 2
    ws.row(8).level = 1
    ws.row(9).level = 1

def write_column_outline_levels(ws):
    ws.col(1).level = 1
    ws.col(2).level = 1
    ws.col(3).level = 2
    ws.col(4).level = 2
    ws.col(5).level = 2
    ws.col(6).level = 2
    ws.col(7).level = 2
    ws.col(8).level = 1
    ws.col(9).level = 1

wb = xlwt.Workbook()

ws0 = wb.add_sheet('Rows Outline')
write_data_cells(ws0)
write_row_outline_levels(ws0)

ws1 = wb.add_sheet('Columns Outline')
write_data_cells(ws1)
write_column_outline_levels(ws1)

ws2 = wb.add_sheet('Rows and Columns Outline')
write_data_cells(ws2)
write_row_outline_levels(ws2)
write_column_outline_levels(ws2)

wb.save('outline.xls')
