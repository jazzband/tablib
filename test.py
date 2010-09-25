# -*- coding: utf-8 -*-

import tablib

data = tablib.Dataset()

data.headers = ['a', 'b', 'c']
data.append([1,2,3])
data.append([1,2,3])

print data.dict

new_data = tablib.formats.json.import_set(str(data.json))
#print new_data.yaml



# data.headers = ['one', 'two', 'three']
# print data.dict