# -*- coding: utf-8 -*-

import tablib

d = tablib.Dataset()

with open('/Users/kreitz/Desktop/test.json') as f:
    d.json = f.read()

# del d[900:]

# print d.height

print len(d.ods)

