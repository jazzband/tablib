# file openpyxl/shared/units.py

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

import math

def pixels_to_EMU(value):
    return int(round(value * 9525))

def EMU_to_pixels(value):
    if not value:
        return 0
    else:
        return round(value / 9525.) 

def EMU_to_cm(value):
    if not value:
        return 0
    else:
        return (EMU_to_pixels(value) * 2.57 / 96) 

def pixels_to_points(value):
    return value * 0.67777777

def points_to_pixels(value):
    if not value:
        return 0
    else:
        return int(math.ceil(value * 1.333333333)) 

def degrees_to_angle(value):
    return int(round(value * 60000))

def angle_to_degrees(value):
    if not value:
        return 0
    else:
        return round(value / 60000.) 

def short_color(color):
    """ format a color to its short size """

    if len(color) > 6:
        return color[2:]
    else:
        return color
