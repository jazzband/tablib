# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

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

wb = Workbook()

ws0 = wb.add_sheet('Rows Outline')

ws0.write_merge(1, 1, 1, 5, 'test 1', style)
ws0.write_merge(2, 2, 1, 4, 'test 1', style)
ws0.write_merge(3, 3, 1, 3, 'test 2', style)
ws0.write_merge(4, 4, 1, 4, 'test 1', style)
ws0.write_merge(5, 5, 1, 4, 'test 3', style)
ws0.write_merge(6, 6, 1, 5, 'test 1', style)
ws0.write_merge(7, 7, 1, 5, 'test 4', style)
ws0.write_merge(8, 8, 1, 4, 'test 1', style)
ws0.write_merge(9, 9, 1, 3, 'test 5', style)

ws0.row(1).level = 1
ws0.row(2).level = 1
ws0.row(3).level = 2
ws0.row(4).level = 2
ws0.row(5).level = 2
ws0.row(6).level = 2
ws0.row(7).level = 2
ws0.row(8).level = 1
ws0.row(9).level = 1


ws1 = wb.add_sheet('Columns Outline')

ws1.write_merge(1, 1, 1, 5, 'test 1', style)
ws1.write_merge(2, 2, 1, 4, 'test 1', style)
ws1.write_merge(3, 3, 1, 3, 'test 2', style)
ws1.write_merge(4, 4, 1, 4, 'test 1', style)
ws1.write_merge(5, 5, 1, 4, 'test 3', style)
ws1.write_merge(6, 6, 1, 5, 'test 1', style)
ws1.write_merge(7, 7, 1, 5, 'test 4', style)
ws1.write_merge(8, 8, 1, 4, 'test 1', style)
ws1.write_merge(9, 9, 1, 3, 'test 5', style)

ws1.col(1).level = 1
ws1.col(2).level = 1
ws1.col(3).level = 2
ws1.col(4).level = 2
ws1.col(5).level = 2
ws1.col(6).level = 2
ws1.col(7).level = 2
ws1.col(8).level = 1
ws1.col(9).level = 1


ws2 = wb.add_sheet('Rows and Columns Outline')

ws2.write_merge(1, 1, 1, 5, 'test 1', style)
ws2.write_merge(2, 2, 1, 4, 'test 1', style)
ws2.write_merge(3, 3, 1, 3, 'test 2', style)
ws2.write_merge(4, 4, 1, 4, 'test 1', style)
ws2.write_merge(5, 5, 1, 4, 'test 3', style)
ws2.write_merge(6, 6, 1, 5, 'test 1', style)
ws2.write_merge(7, 7, 1, 5, 'test 4', style)
ws2.write_merge(8, 8, 1, 4, 'test 1', style)
ws2.write_merge(9, 9, 1, 3, 'test 5', style)

ws2.row(1).level = 1
ws2.row(2).level = 1
ws2.row(3).level = 2
ws2.row(4).level = 2
ws2.row(5).level = 2
ws2.row(6).level = 2
ws2.row(7).level = 2
ws2.row(8).level = 1
ws2.row(9).level = 1

ws2.col(1).level = 1
ws2.col(2).level = 1
ws2.col(3).level = 2
ws2.col(4).level = 2
ws2.col(5).level = 2
ws2.col(6).level = 2
ws2.col(7).level = 2
ws2.col(8).level = 1
ws2.col(9).level = 1


ws0.protect = True
ws0.wnd_protect = True
ws0.obj_protect = True
ws0.scen_protect = True
ws0.password = "123456"

ws1.protect = True
ws1.wnd_protect = True
ws1.obj_protect = True
ws1.scen_protect = True
ws1.password = "abcdefghij"

ws2.protect = True
ws2.wnd_protect = True
ws2.obj_protect = True
ws2.scen_protect = True
ws2.password = "ok"

wb.protect = True
wb.wnd_protect = True
wb.obj_protect = True
wb.save('protection.xls')
