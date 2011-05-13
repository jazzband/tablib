# file openpyxl/shared/date_time.py

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

"""Manage Excel date weirdness."""

# Python stdlib imports

from math import floor
import calendar
import datetime
import time
import re

# constants
W3CDTF_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

RE_W3CDTF = '(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(.(\d{2}))?Z'

EPOCH = datetime.datetime.utcfromtimestamp(0)

def datetime_to_W3CDTF(dt):
    """Convert from a datetime to a timestamp string."""
    return datetime.datetime.strftime(dt, W3CDTF_FORMAT)


def W3CDTF_to_datetime(formatted_string):
    """Convert from a timestamp string to a datetime object."""
    match = re.match(RE_W3CDTF,formatted_string)
    digits = list(map(int, match.groups()[:6]))
    return datetime.datetime(*digits)


class SharedDate(object):
    """Date formatting utilities for Excel with shared state.

    Excel has a two primary date tracking schemes:
      Windows - Day 1 == 1900-01-01
      Mac - Day 1 == 1904-01-01

    SharedDate stores which system we are using and converts dates between
    Python and Excel accordingly.

    """
    CALENDAR_WINDOWS_1900 = 1900
    CALENDAR_MAC_1904 = 1904
    datetime_object_type = 'DateTime'

    def __init__(self):
        self.excel_base_date = self.CALENDAR_WINDOWS_1900

    def datetime_to_julian(self, date):
        """Convert from python datetime to excel julian date representation."""

        if isinstance(date, datetime.datetime):
            return self.to_julian(date.year, date.month, date.day, \
                hours=date.hour, minutes=date.minute, seconds=date.second)
        elif isinstance(date, datetime.date):
            return self.to_julian(date.year, date.month, date.day)

    def to_julian(self, year, month, day, hours=0, minutes=0, seconds=0):
        """Convert from Python date to Excel JD."""
        # explicitly disallow bad years
        # Excel 2000 treats JD=0 as 1/0/1900 (buggy, disallow)
        # Excel 2000 treats JD=2958466 as a bad date (Y10K bug!)
        if year < 1900 or year > 10000:
            msg = 'Year not supported by Excel: %s' % year
            raise ValueError(msg)
        if self.excel_base_date == self.CALENDAR_WINDOWS_1900:
            # Fudge factor for the erroneous fact that the year 1900 is
            # treated as a Leap Year in MS Excel.  This affects every date
            # following 28th February 1900
            if year == 1900 and month <= 2:
                excel_1900_leap_year = False
            else:
                excel_1900_leap_year = True
            excel_base_date = 2415020
        else:
            raise NotImplementedError('Mac dates are not yet supported.')
            #excel_base_date = 2416481
            #excel_1900_leap_year = False

        # Julian base date adjustment
        if month > 2:
            month = month - 3
        else:
            month = month + 9
            year -= 1

        # Calculate the Julian Date, then subtract the Excel base date
        # JD 2415020 = 31 - Dec - 1899 -> Excel Date of 0
        century, decade = int(str(year)[:2]), int(str(year)[2:])
        excel_date = floor(146097 * century / 4) + \
                floor((1461 * decade) / 4) + floor((153 * month + 2) / 5) + \
                day + 1721119 - excel_base_date
        if excel_1900_leap_year:
            excel_date += 1

        # check to ensure that we exclude 2/29/1900 as a possible value
        if self.excel_base_date == self.CALENDAR_WINDOWS_1900 \
                and excel_date == 60:
            msg = 'Error: Excel believes 1900 was a leap year'
            raise ValueError(msg)
        excel_time = ((hours * 3600) + (minutes * 60) + seconds) / 86400
        return excel_date + excel_time

    def from_julian(self, value=0):
        """Convert from the Excel JD back to a date"""
        if self.excel_base_date == self.CALENDAR_WINDOWS_1900:
            excel_base_date = 25569
            if value < 60:
                excel_base_date -= 1
            elif value == 60:
                msg = 'Error: Excel believes 1900 was a leap year'
                raise ValueError(msg)
        else:
            raise NotImplementedError('Mac dates are not yet supported.')
            #excel_base_date = 24107

        if value >= 1:
            utc_days = value - excel_base_date

            return EPOCH + datetime.timedelta(days=utc_days)

        elif value >= 0:
            hours = floor(value * 24)
            mins = floor(value * 24 * 60) - floor(hours * 60)
            secs = floor(value * 24 * 60 * 60) - floor(hours * 60 * 60) - \
                    floor(mins * 60)
            return datetime.time(int(hours), int(mins), int(secs))
        else:
            msg = 'Negative dates (%s) are not supported' % value
            raise ValueError(msg)
