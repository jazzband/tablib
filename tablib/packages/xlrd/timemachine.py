# -*- coding: cp1252 -*-

##
# <p>Copyright © 2006-2008 Stephen John Machin, Lingfo Pty Ltd</p>
# <p>This module is part of the xlrd package, which is released under a BSD-style licence.</p>
##

# timemachine.py -- adaptation for earlier Pythons e.g. 2.1
# usage: from timemachine import *

# 2008-02-08 SJM Generalised method of detecting IronPython

import sys

python_version = sys.version_info[:2] # e.g. version 2.4 -> (2, 4)

CAN_PICKLE_ARRAY = python_version >= (2, 5)
CAN_SUBCLASS_BUILTIN = python_version >= (2, 2)

if sys.version.find("IronPython") >= 0:
    array_array = None
else:
    from array import array as array_array

if python_version < (2, 2):
    class object:
        pass
    False = 0
    True = 1

def int_floor_div(x, y):
    return divmod(x, y)[0]

def intbool(x):
    if x:
        return 1
    return 0

if python_version < (2, 3):
    def sum(sequence, start=0):
        tot = start
        for item in aseq:
            tot += item
        return tot
