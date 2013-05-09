# file openpyxl/namedrange.py

# Copyright (c) 2010-2011 openpyxl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: see AUTHORS file

"""Track named groups of cells in a worksheet"""

# Python stdlib imports
import re

# package imports
from openpyxl.shared.compat import unicode
from openpyxl.shared.exc import NamedRangeException

# constants
NAMED_RANGE_RE = re.compile("^(('(?P<quoted>([^']|'')*)')|(?P<notquoted>[^']*))!(?P<range>(\$([A-Za-z]+))?\$([0-9]+)(:(\$([A-Za-z]+))?(\$([0-9]+)))?)")
SPLIT_NAMED_RANGE_RE = re.compile(r"((?:[^,']|'(?:[^']|'')*')+)")

class NamedRange(object):
    """A named group of cells
    
    Scope is a worksheet object or None for workbook scope names (the default)
    """
    __slots__ = ('name', 'destinations', 'scope')

    str_format = unicode('%s!%s')
    repr_format = unicode('<%s "%s">')

    def __init__(self, name, destinations):
        self.name = name
        self.destinations = destinations
        self.scope = None

    def __str__(self):
        return  ','.join([self.str_format % (sheet, name) for sheet, name in self.destinations])

    def __repr__(self):

        return  self.repr_format % (self.__class__.__name__, str(self))

class NamedRangeContainingValue(object):
    """A named value"""
    __slots__ = ('name', 'value', 'scope')

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.scope = None


def split_named_range(range_string):
    """Separate a named range into its component parts"""

    destinations = []
    for range_string in SPLIT_NAMED_RANGE_RE.split(range_string)[1::2]: # Skip first and from there every second item

        match = NAMED_RANGE_RE.match(range_string)
        if not match:
            raise NamedRangeException('Invalid named range string: "%s"' % range_string)
        else:
            match = match.groupdict()
            sheet_name = match['quoted'] or match['notquoted']
            xlrange = match['range']
            sheet_name = sheet_name.replace("''", "'") # Unescape '
            destinations.append((sheet_name, xlrange))
            
    return destinations

def refers_to_range(range_string):
    return bool(NAMED_RANGE_RE.match(range_string))
