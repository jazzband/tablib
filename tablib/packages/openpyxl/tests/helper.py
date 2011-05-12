# file openpyxl/tests/helper.py

# Copyright (c) 2010 openpyxl
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
# @author: Eric Gazoni

# Python stdlib imports
from __future__ import with_statement
import os
import os.path
import shutil
import difflib
from StringIO import StringIO
from pprint import pprint
from tempfile import gettempdir

# package imports
from openpyxl.shared.xmltools import fromstring, ElementTree
from openpyxl.shared.xmltools import pretty_indent

# constants
DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data'))
TMPDIR = os.path.join(gettempdir(), 'openpyxl_test_temp')


def make_tmpdir():
    try:
        os.makedirs(TMPDIR)
    except OSError:
        pass


def clean_tmpdir():
    if os.path.isdir(TMPDIR):
        shutil.rmtree(TMPDIR, ignore_errors = True)


def assert_equals_file_content(reference_file, fixture, filetype = 'xml'):
    if os.path.isfile(fixture):
        with open(fixture) as fixture_file:
            fixture_content = fixture_file.read()
    else:
        fixture_content = fixture

    with open(reference_file) as expected_file:
        expected_content = expected_file.read()

    if filetype == 'xml':
        fixture_content = fromstring(fixture_content)
        pretty_indent(fixture_content)
        temp = StringIO()
        ElementTree(fixture_content).write(temp)
        fixture_content = temp.getvalue()

        expected_content = fromstring(expected_content)
        pretty_indent(expected_content)
        temp = StringIO()
        ElementTree(expected_content).write(temp)
        expected_content = temp.getvalue()

    fixture_lines = fixture_content.split('\n')
    expected_lines = expected_content.split('\n')
    differences = list(difflib.unified_diff(expected_lines, fixture_lines))
    if differences:
        temp = StringIO()
        pprint(differences, stream = temp)
        assert False, 'Differences found : %s' % temp.getvalue()

def get_xml(xml_node):

    io = StringIO()
    ElementTree(xml_node).write(io, encoding = 'UTF-8')
    ret = io.getvalue()
    io.close()
    return ret.replace('\n', '')
