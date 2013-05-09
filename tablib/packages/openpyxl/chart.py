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

import math

from openpyxl.style import NumberFormat
from openpyxl.drawing import Drawing, Shape
from openpyxl.shared.units import pixels_to_EMU, short_color
from openpyxl.cell import get_column_letter

class Axis(object):

    POSITION_BOTTOM = 'b'
    POSITION_LEFT = 'l'

    ORIENTATION_MIN_MAX = "minMax"

    def __init__(self):

        self.orientation = self.ORIENTATION_MIN_MAX
        self.number_format = NumberFormat()
        for attr in ('position', 'tick_label_position', 'crosses',
            'auto', 'label_align', 'label_offset', 'cross_between'):
            setattr(self, attr, None)
        self.min = 0
        self.max = None
        self.unit = None
        self.title = ''

    @classmethod
    def default_category(cls):
        """ default values for category axes """

        ax = Axis()
        ax.id = 60871424
        ax.cross = 60873344
        ax.position = Axis.POSITION_BOTTOM
        ax.tick_label_position = 'nextTo'
        ax.crosses = "autoZero"
        ax.auto = True
        ax.label_align = 'ctr'
        ax.label_offset = 100
        return ax

    @classmethod
    def default_value(cls):
        """ default values for value axes """

        ax = Axis()
        ax.id = 60873344
        ax.cross = 60871424
        ax.position = Axis.POSITION_LEFT
        ax.major_gridlines = None
        ax.tick_label_position = 'nextTo'
        ax.crosses = 'autoZero'
        ax.auto = False
        ax.cross_between = 'between'
        return ax

class Reference(object):
    """ a simple wrapper around a serie of reference data """

    def __init__(self, sheet, pos1, pos2=None):

        self.sheet = sheet
        self.pos1 = pos1
        self.pos2 = pos2

    def get_type(self):

        if isinstance(self.values[0], basestring):
            return 'str'
        else:
            return 'num'

    @property
    def values(self):
        """ read data in sheet - to be used at writing time """
        if hasattr(self, "values"):
            return self._values
        if self.pos2 is None:
            cell = self.sheet.cell(row=self.pos1[0], column=self.pos1[1])
            self._values = [cell.value]
        else:
            self._values = []
            for row in range(int(self.pos1[0]), int(self.pos2[0] + 1)):
                for col in range(int(self.pos1[1]), int(self.pos2[1] + 1)):
                    self._values.append(self.sheet.cell(row=row, column=col).value)
        return self._values

    def _get_ref(self):
        """ legace method """
        return str(self)

    def __str__(self):
        """ format excel reference notation """

        if self.pos2:
            return "'%s'!$%s$%s:$%s$%s" % (self.sheet.title,
                get_column_letter(self.pos1[1] + 1), self.pos1[0] + 1,
                get_column_letter(self.pos2[1] + 1), self.pos2[0] + 1)
        else:
            return "'%s'!$%s$%s" % (self.sheet.title,
                get_column_letter(self.pos1[1] + 1), self.pos1[0] + 1)

    def _get_cache(self):
        """ legacy method """
        return self.values



class Serie(object):
    """ a serie of data and possibly associated labels """

    MARKER_NONE = 'none'

    def __init__(self, values, labels=None, legend=None, color=None, xvalues=None):

        self.marker = Serie.MARKER_NONE
        self.values = values
        self.xvalues = xvalues
        self.labels = labels
        self.legend = legend
        self.error_bar = None

    @property
    def color(self):
        return getattr(self, "_color", None)

    @color.setter
    def color(self, color):
        if color is None:
            raise ValueError("Colors must be strings of the format XXXXX")
        self._color = short_color(color)

    @property
    def values(self):
        """Return values from underlying reference"""
        return self._values

    @values.setter
    def values(self, reference):
        """Assign values from reference to serie"""
        if reference is not None:
            if not isinstance(reference, Reference):
                raise TypeError("Series values must be a Reference instance")
            self._values = reference.values
        else:
            self._values = None
        self.reference = reference

    @property
    def xvalues(self):
        """Return xvalues"""
        return self._xvalues

    @xvalues.setter
    def xvalues(self, reference):
        if reference is not None:
            if not isinstance(reference, Reference):
                raise TypeError("Series xvalues must be a Reference instance")
            self._xvalues = reference.values
        else:
            self._xvalues = None
        self.xreference = reference

    def mymax(self, values):
        return max([x for x in values])

    def get_min_max(self):

        if self.error_bar:
            err_cache = self.error_bar.values
            vals = [v + err_cache[i] \
                for i, v in enumerate(self.values)]
        else:
            vals = self.values
        return min(vals), self.mymax(vals)

    def __len__(self):

        return len(self.values)

class Legend(object):

    def __init__(self):

        self.position = 'r'
        self.layout = None

class ErrorBar(object):

    PLUS = 1
    MINUS = 2
    PLUS_MINUS = 3

    def __init__(self, _type, values):

        self.type = _type
        self.values = values

    @property
    def values(self):
        """Return values from underlying reference"""
        return self._values

    @values.setter
    def values(self, reference):
        """Assign values from reference to serie"""
        if reference is not None:
            if not isinstance(reference, Reference):
                raise TypeError("Errorbar values must be a Reference instance")
            self._values = reference.values
        else:
            self._values = None
        self.reference = reference

class Chart(object):
    """ raw chart class """

    GROUPING_CLUSTERED = 'clustered'
    GROUPING_STANDARD = 'standard'

    BAR_CHART = 1
    LINE_CHART = 2
    SCATTER_CHART = 3

    def mymax(self, values):
        return max([x for x in values if x])

    def __init__(self, _type, grouping):

        self._series = []

        # public api
        self.type = _type
        self.grouping = grouping
        self.x_axis = Axis.default_category()
        self.y_axis = Axis.default_value()
        self.legend = Legend()
        self.show_legend = True
        self.lang = 'fr-FR'
        self.title = ''
        self.print_margins = dict(b=.75, l=.7, r=.7, t=.75, header=0.3, footer=.3)

        # the containing drawing
        self.drawing = Drawing()

        # the offset for the plot part in percentage of the drawing size
        self.width = .6
        self.height = .6
        self.margin_top = self._get_max_margin_top()
        self.margin_left = 0

        # the user defined shapes
        self._shapes = []

    def add_serie(self, serie):

        serie.id = len(self._series)
        self._series.append(serie)
        self._compute_min_max()
        if not None in [s.xvalues for s in self._series]:
            self._compute_xmin_xmax()

    def add_shape(self, shape):

        shape._chart = self
        self._shapes.append(shape)

    def get_x_units(self):
        """ calculate one unit for x axis in EMU """

        return self.mymax([len(s.values) for s in self._series])

    def get_y_units(self):
        """ calculate one unit for y axis in EMU """

        dh = pixels_to_EMU(self.drawing.height)
        return (dh * self.height) / self.y_axis.max

    def get_y_chars(self):
        """ estimate nb of chars for y axis """

        _max = max([self.mymax(s.values) for s in self._series])
        return len(str(int(_max)))

    def _compute_min_max(self):
        """ compute y axis limits and units """

        maxi = max([self.mymax(s.values) for s in self._series if s.values])

        mul = None
        if maxi < 1:
            s = str(maxi).split('.')[1]
            mul = 10.0
            for x in s:
                if x == '0':
                    mul *= 10.0
                else:
                    break
            maxi = maxi * mul

        maxi = math.ceil(float(maxi) * 1.1)
        sz = len(str(int(maxi))) - 1
        unit = math.ceil(math.ceil(float(maxi) / pow(10.0, sz)) * pow(10.0, sz - 1))
        maxi = math.ceil(float(maxi) / unit) * unit

        if mul is not None:
            maxi = maxi / mul
            unit = unit / mul

        if maxi / unit > 9:
            # no more that 10 ticks
            unit *= 2

        self.y_axis.max = maxi
        self.y_axis.unit = unit

    def _compute_xmin_xmax(self):
        """ compute x axis limits and units """

        maxi = max([self.mymax(s.xvalues) for s in self._series])

        mul = None
        if maxi < 1:
            s = str(maxi).split('.')[1]
            mul = 10
            for x in s:
                if x == '0':
                    mul *= 10
                else:
                    break
            maxi = maxi * mul

        maxi = math.ceil(maxi * 1.1)
        sz = len(str(int(maxi))) - 1
        unit = math.ceil(math.ceil(maxi / pow(10, sz)) * pow(10, sz - 1))
        maxi = math.ceil(maxi / unit) * unit

        if mul is not None:
            maxi = maxi / mul
            unit = unit / mul

        if maxi / unit > 9:
            # no more that 10 ticks
            unit *= 2

        self.x_axis.max = maxi
        self.x_axis.unit = unit

    def _get_max_margin_top(self):

        mb = Shape.FONT_HEIGHT + Shape.MARGIN_BOTTOM
        plot_height = self.drawing.height * self.height
        return float(self.drawing.height - plot_height - mb) / self.drawing.height

    def _get_min_margin_left(self):

        ml = (self.get_y_chars() * Shape.FONT_WIDTH) + Shape.MARGIN_LEFT
        return float(ml) / self.drawing.width

    def _get_margin_top(self):
        """ get margin in percent """

        return min(self.margin_top, self._get_max_margin_top())

    def _get_margin_left(self):

        return max(self._get_min_margin_left(), self.margin_left)

class BarChart(Chart):
    def __init__(self):
        super(BarChart, self).__init__(Chart.BAR_CHART, Chart.GROUPING_CLUSTERED)

class LineChart(Chart):
    def __init__(self):
        super(LineChart, self).__init__(Chart.LINE_CHART, Chart.GROUPING_STANDARD)

class ScatterChart(Chart):
    def __init__(self):
        super(ScatterChart, self).__init__(Chart.SCATTER_CHART, Chart.GROUPING_STANDARD)


