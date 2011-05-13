import tablib

d = tablib.Dataset()

d.headers = ['face', 'book']
d.append([1,2])

f = open('test.xlsx', 'wb')
f.write(d.xlsx)