# -*- coding: ascii -*-

##
# <p>Copyright (c) 2006-2012 Stephen John Machin, Lingfo Pty Ltd</p>
# <p>This module is part of the xlrd package, which is released under a BSD-style licence.</p>
##

# timemachine.py -- adaptation for single codebase.
# Currently supported: 2.1 to 2.7
# usage: from timemachine import *

from __future__ import nested_scopes
import sys

python_version = sys.version_info[:2] # e.g. version 2.4 -> (2, 4)

CAN_PICKLE_ARRAY = python_version >= (2, 5)

if python_version >= (3, 0):
    # Python 3
    BYTES_LITERAL = lambda x: x.encode('latin1')
    UNICODE_LITERAL = lambda x: x
    BYTES_ORD = lambda byte: byte
    from io import BytesIO as BYTES_IO
    def fprintf(f, fmt, *vargs):
        fmt = fmt.replace("%r", "%a")
        f.write(fmt % vargs)
    EXCEL_TEXT_TYPES = (str, bytes, bytearray) # xlwt: isinstance(obj, EXCEL_TEXT_TYPES)
    REPR = ascii
    xrange = range
    unicode = lambda b, enc: b.decode(enc)
else:
    # Python 2
    BYTES_LITERAL = lambda x: x
    UNICODE_LITERAL = lambda x: x.decode('latin1')
    BYTES_ORD = ord
    from cStringIO import StringIO as BYTES_IO
    def fprintf(f, fmt, *vargs):
        f.write(fmt % vargs)
    try:
        EXCEL_TEXT_TYPES = basestring # xlwt: isinstance(obj, EXCEL_TEXT_TYPES)
    except NameError:
        EXCEL_TEXT_TYPES = (str, unicode)
    REPR = repr
    xrange = xrange

if python_version >= (2, 6):
    def BUFFER(obj, offset=0, size=None):
        if size is None:
            return memoryview(obj)[offset:]
        return memoryview(obj)[offset:offset+size]
else:
    BUFFER = buffer

try:
    from array import array as array_array
except ImportError:
    # old version of IronPython?
    array_array = None

try:
    object
except NameError:
    class object:
        pass

try:
    True
except NameError:
    setattr(sys.modules['__builtin__'], 'True', 1)

try:
    False
except NameError:
    setattr(sys.modules['__builtin__'], 'False', 0)
    
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
