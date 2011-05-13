'''
Copyright (c) 2010 openpyxl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@license: http://www.opensource.org/licenses/mit-license.php
@author: Eric Gazoni
'''

import math
from .style import Color
from .shared.units import pixels_to_EMU, EMU_to_pixels, short_color

class Shadow(object):

    SHADOW_BOTTOM = 'b'
    SHADOW_BOTTOM_LEFT = 'bl'
    SHADOW_BOTTOM_RIGHT = 'br'
    SHADOW_CENTER = 'ctr'
    SHADOW_LEFT = 'l'
    SHADOW_TOP = 't'
    SHADOW_TOP_LEFT = 'tl'
    SHADOW_TOP_RIGHT = 'tr'

    def __init__(self):
    	self.visible = False
    	self.blurRadius = 6
    	self.distance = 2
    	self.direction = 0
    	self.alignment = self.SHADOW_BOTTOM_RIGHT
    	self.color = Color(Color.BLACK)
    	self.alpha = 50

class Drawing(object):
    """ a drawing object - eg container for shapes or charts
        we assume user specifies dimensions in pixels; units are
        converted to EMU in the drawing part
    """

    count = 0

    def __init__(self):

        self.name = ''
        self.description = ''
        self.coordinates = ((1,2), (16,8))
        self.left = 0
        self.top = 0
        self._width = EMU_to_pixels(200000)
        self._height = EMU_to_pixels(1828800)
        self.resize_proportional = False
        self.rotation = 0
#        self.shadow = Shadow()

    def _set_width(self, w):

        if self.resize_proportional and w:
            ratio = self._height / self._width
            self._height = round(ratio * w)
        self._width = w

    def _get_width(self):

        return self._width

    width = property(_get_width, _set_width)

    def _set_height(self, h):

        if self.resize_proportional and h:
            ratio = self._width / self._height
            self._width = round(ratio * h)
        self._height = h

    def _get_height(self):

        return self._height

    height = property(_get_height, _set_height)

    def set_dimension(self, w=0, h=0):

        xratio = w / self._width
        yratio = h / self._height

        if self.resize_proportional and w and h:
            if (xratio * self._height) < h:
                self._height = math.ceil(xratio * self._height)
                self._width = width
            else:
                self._width	= math.ceil(yratio * self._width)
                self._height = height

    def get_emu_dimensions(self):
        """ return (x, y, w, h) in EMU """

        return (pixels_to_EMU(self.left), pixels_to_EMU(self.top),
            pixels_to_EMU(self._width), pixels_to_EMU(self._height))


class Shape(object):
    """ a drawing inside a chart
        coordiantes are specified by the user in the axis units
    """

    MARGIN_LEFT = 6 + 13 + 1
    MARGIN_BOTTOM = 17 + 11

    FONT_WIDTH = 7
    FONT_HEIGHT = 8

    ROUND_RECT = 'roundRect'
    RECT = 'rect'

    # other shapes to define :
    '''
    "line"
    "lineInv"
    "triangle"
    "rtTriangle"
    "diamond"
    "parallelogram"
    "trapezoid"
    "nonIsoscelesTrapezoid"
    "pentagon"
    "hexagon"
    "heptagon"
    "octagon"
    "decagon"
    "dodecagon"
    "star4"
    "star5"
    "star6"
    "star7"
    "star8"
    "star10"
    "star12"
    "star16"
    "star24"
    "star32"
    "roundRect"
    "round1Rect"
    "round2SameRect"
    "round2DiagRect"
    "snipRoundRect"
    "snip1Rect"
    "snip2SameRect"
    "snip2DiagRect"
    "plaque"
    "ellipse"
    "teardrop"
    "homePlate"
    "chevron"
    "pieWedge"
    "pie"
    "blockArc"
    "donut"
    "noSmoking"
    "rightArrow"
    "leftArrow"
    "upArrow"
    "downArrow"
    "stripedRightArrow"
    "notchedRightArrow"
    "bentUpArrow"
    "leftRightArrow"
    "upDownArrow"
    "leftUpArrow"
    "leftRightUpArrow"
    "quadArrow"
    "leftArrowCallout"
    "rightArrowCallout"
    "upArrowCallout"
    "downArrowCallout"
    "leftRightArrowCallout"
    "upDownArrowCallout"
    "quadArrowCallout"
    "bentArrow"
    "uturnArrow"
    "circularArrow"
    "leftCircularArrow"
    "leftRightCircularArrow"
    "curvedRightArrow"
    "curvedLeftArrow"
    "curvedUpArrow"
    "curvedDownArrow"
    "swooshArrow"
    "cube"
    "can"
    "lightningBolt"
    "heart"
    "sun"
    "moon"
    "smileyFace"
    "irregularSeal1"
    "irregularSeal2"
    "foldedCorner"
    "bevel"
    "frame"
    "halfFrame"
    "corner"
    "diagStripe"
    "chord"
    "arc"
    "leftBracket"
    "rightBracket"
    "leftBrace"
    "rightBrace"
    "bracketPair"
    "bracePair"
    "straightConnector1"
    "bentConnector2"
    "bentConnector3"
    "bentConnector4"
    "bentConnector5"
    "curvedConnector2"
    "curvedConnector3"
    "curvedConnector4"
    "curvedConnector5"
    "callout1"
    "callout2"
    "callout3"
    "accentCallout1"
    "accentCallout2"
    "accentCallout3"
    "borderCallout1"
    "borderCallout2"
    "borderCallout3"
    "accentBorderCallout1"
    "accentBorderCallout2"
    "accentBorderCallout3"
    "wedgeRectCallout"
    "wedgeRoundRectCallout"
    "wedgeEllipseCallout"
    "cloudCallout"
    "cloud"
    "ribbon"
    "ribbon2"
    "ellipseRibbon"
    "ellipseRibbon2"
    "leftRightRibbon"
    "verticalScroll"
    "horizontalScroll"
    "wave"
    "doubleWave"
    "plus"
    "flowChartProcess"
    "flowChartDecision"
    "flowChartInputOutput"
    "flowChartPredefinedProcess"
    "flowChartInternalStorage"
    "flowChartDocument"
    "flowChartMultidocument"
    "flowChartTerminator"
    "flowChartPreparation"
    "flowChartManualInput"
    "flowChartManualOperation"
    "flowChartConnector"
    "flowChartPunchedCard"
    "flowChartPunchedTape"
    "flowChartSummingJunction"
    "flowChartOr"
    "flowChartCollate"
    "flowChartSort"
    "flowChartExtract"
    "flowChartMerge"
    "flowChartOfflineStorage"
    "flowChartOnlineStorage"
    "flowChartMagneticTape"
    "flowChartMagneticDisk"
    "flowChartMagneticDrum"
    "flowChartDisplay"
    "flowChartDelay"
    "flowChartAlternateProcess"
    "flowChartOffpageConnector"
    "actionButtonBlank"
    "actionButtonHome"
    "actionButtonHelp"
    "actionButtonInformation"
    "actionButtonForwardNext"
    "actionButtonBackPrevious"
    "actionButtonEnd"
    "actionButtonBeginning"
    "actionButtonReturn"
    "actionButtonDocument"
    "actionButtonSound"
    "actionButtonMovie"
    "gear6"
    "gear9"
    "funnel"
    "mathPlus"
    "mathMinus"
    "mathMultiply"
    "mathDivide"
    "mathEqual"
    "mathNotEqual"
    "cornerTabs"
    "squareTabs"
    "plaqueTabs"
    "chartX"
    "chartStar"
    "chartPlus"
    '''

    def __init__(self, coordinates=((0,0), (1,1)), text=None, scheme="accent1"):

        self.coordinates = coordinates # in axis unit
        self.text = text
        self.scheme = scheme
        self.style = Shape.RECT
        self._border_width = 3175 # in EMU
        self._border_color = Color.BLACK[2:] #"F3B3C5"
        self._color = Color.WHITE[2:]
        self._text_color = Color.BLACK[2:]

    def _get_border_color(self):
        return self._border_color

    def _set_border_color(self, color):
        self._border_color = short_color(color)

    border_color = property(_get_border_color, _set_border_color)

    def _get_color(self):
        return self._color

    def _set_color(self, color):
        self._color = short_color(color)

    color = property(_get_color, _set_color)

    def _get_text_color(self):
        return self._text_color

    def _set_text_color(self, color):
        self._text_color = short_color(color)

    text_color = property(_get_text_color, _set_text_color)

    def _get_border_width(self):

        return EMU_to_pixels(self._border_width)

    def _set_border_width(self, w):

        self._border_width = pixels_to_EMU(w)
        # print self._border_width

    border_width = property(_get_border_width, _set_border_width)

    def get_coordinates(self):
        """ return shape coordinates in percentages (left, top, right, bottom) """

        (x1, y1), (x2, y2) = self.coordinates

        drawing_width = pixels_to_EMU(self._chart.drawing.width)
        drawing_height = pixels_to_EMU(self._chart.drawing.height)
        plot_width = drawing_width * self._chart.width
        plot_height = drawing_height * self._chart.height

        margin_left = self._chart._get_margin_left() * drawing_width
        xunit = plot_width / self._chart.get_x_units()

        margin_top = self._chart._get_margin_top() * drawing_height
        yunit = self._chart.get_y_units()

        x_start = (margin_left + (float(x1) * xunit)) / drawing_width
        y_start = (margin_top + plot_height - (float(y1) * yunit)) / drawing_height

        x_end = (margin_left + (float(x2) * xunit)) / drawing_width
        y_end = (margin_top + plot_height - (float(y2) * yunit)) / drawing_height

        def _norm_pct(pct):
            """ force shapes to appear by truncating too large sizes """
            if pct>1: pct = 1
            elif pct<0: pct = 0
            return pct

        # allow user to specify y's in whatever order
        # excel expect y_end to be lower
        if y_end < y_start:
            y_end, y_start = y_start, y_end

        return (_norm_pct(x_start), _norm_pct(y_start),
            _norm_pct(x_end), _norm_pct(y_end))
