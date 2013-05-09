# Copyright (c) 2001-2011 Python Software Foundation
#
# License: PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
#          See http://www.opensource.org/licenses/Python-2.0 for full terms

import sys

if sys.version_info < (2, 5):
    def all(iterable):
        for element in iterable:
            if not element:
                return False
        return True

    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False
else:
    all = all
    any = any

del sys
