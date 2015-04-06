# -*- coding: cp1252 -*-

# No part of the content of this file was derived from the works of David Giffin.

##
# <p>Copyright © 2005-2008 Stephen John Machin, Lingfo Pty Ltd</p>
# <p>This module is part of the xlrd package, which is released under a BSD-style licence.</p>
#
# <p>Provides function(s) for dealing with Microsoft Excel ™ dates.</p>
##

# 2008-10-18 SJM Fix bug in xldate_from_date_tuple (affected some years after 2099)

# The conversion from days to (year, month, day) starts with
# an integral "julian day number" aka JDN.
# FWIW, JDN 0 corresponds to noon on Monday November 24 in Gregorian year -4713.
# More importantly:
#    Noon on Gregorian 1900-03-01 (day 61 in the 1900-based system) is JDN 2415080.0
#    Noon on Gregorian 1904-01-02 (day  1 in the 1904-based system) is JDN 2416482.0
import datetime

_JDN_delta = (2415080 - 61, 2416482 - 1)
assert _JDN_delta[1] - _JDN_delta[0] == 1462

# Pre-calculate the datetime epochs for efficiency.
epoch_1904 = datetime.datetime(1904, 1, 1)
epoch_1900 = datetime.datetime(1899, 12, 31)
epoch_1900_minus_1 = datetime.datetime(1899, 12, 30)

class XLDateError(ValueError): pass

class XLDateNegative(XLDateError): pass
class XLDateAmbiguous(XLDateError): pass
class XLDateTooLarge(XLDateError): pass
class XLDateBadDatemode(XLDateError): pass
class XLDateBadTuple(XLDateError): pass

_XLDAYS_TOO_LARGE = (2958466, 2958466 - 1462) # This is equivalent to 10000-01-01

##
# Convert an Excel number (presumed to represent a date, a datetime or a time) into
# a tuple suitable for feeding to datetime or mx.DateTime constructors.
# @param xldate The Excel number
# @param datemode 0: 1900-based, 1: 1904-based.
# <br>WARNING: when using this function to
# interpret the contents of a workbook, you should pass in the Book.datemode
# attribute of that workbook. Whether
# the workbook has ever been anywhere near a Macintosh is irrelevant.
# @return Gregorian (year, month, day, hour, minute, nearest_second).
# <br>Special case: if 0.0 <= xldate < 1.0, it is assumed to represent a time;
# (0, 0, 0, hour, minute, second) will be returned.
# <br>Note: 1904-01-01 is not regarded as a valid date in the datemode 1 system; its "serial number"
# is zero.
# @throws XLDateNegative xldate < 0.00
# @throws XLDateAmbiguous The 1900 leap-year problem (datemode == 0 and 1.0 <= xldate < 61.0)
# @throws XLDateTooLarge Gregorian year 10000 or later
# @throws XLDateBadDatemode datemode arg is neither 0 nor 1
# @throws XLDateError Covers the 4 specific errors

def xldate_as_tuple(xldate, datemode):
    if datemode not in (0, 1):
        raise XLDateBadDatemode(datemode)
    if xldate == 0.00:
        return (0, 0, 0, 0, 0, 0)
    if xldate < 0.00:
        raise XLDateNegative(xldate)
    xldays = int(xldate)
    frac = xldate - xldays
    seconds = int(round(frac * 86400.0))
    assert 0 <= seconds <= 86400
    if seconds == 86400:
        hour = minute = second = 0
        xldays += 1
    else:
        # second = seconds % 60; minutes = seconds // 60
        minutes, second = divmod(seconds, 60)
        # minute = minutes % 60; hour    = minutes // 60
        hour, minute = divmod(minutes, 60)
    if xldays >= _XLDAYS_TOO_LARGE[datemode]:
        raise XLDateTooLarge(xldate)

    if xldays == 0:
        return (0, 0, 0, hour, minute, second)

    if xldays < 61 and datemode == 0:
        raise XLDateAmbiguous(xldate)

    jdn = xldays + _JDN_delta[datemode]
    yreg = ((((jdn * 4 + 274277) // 146097) * 3 // 4) + jdn + 1363) * 4 + 3
    mp = ((yreg % 1461) // 4) * 535 + 333
    d = ((mp % 16384) // 535) + 1
    # mp /= 16384
    mp >>= 14
    if mp >= 10:
        return ((yreg // 1461) - 4715, mp - 9, d, hour, minute, second)
    else:
        return ((yreg // 1461) - 4716, mp + 3, d, hour, minute, second)


##
# Convert an Excel date/time number into a datetime.datetime object.
#
# @param xldate The Excel number
# @param datemode 0: 1900-based, 1: 1904-based.
#
# @return a datetime.datetime() object.
#
def xldate_as_datetime(xldate, datemode):
    """Convert an Excel date/time number into a datetime.datetime object."""

    # Set the epoch based on the 1900/1904 datemode.
    if datemode:
        epoch = epoch_1904
    else:
        if xldate < 60:
            epoch = epoch_1900
        else:
            # Workaround Excel 1900 leap year bug by adjusting the epoch.
            epoch = epoch_1900_minus_1

    # The integer part of the Excel date stores the number of days since
    # the epoch and the fractional part stores the percentage of the day.
    days = int(xldate)
    fraction = xldate - days

    # Get the the integer and decimal seconds in Excel's millisecond resolution.
    seconds = int(round(fraction * 86400000.0))
    seconds, milliseconds = divmod(seconds, 1000)

    return epoch + datetime.timedelta(days, seconds, 0, milliseconds)


# === conversions from date/time to xl numbers

def _leap(y):
    if y % 4: return 0
    if y % 100: return 1
    if y % 400: return 0
    return 1

_days_in_month = (None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

##
# Convert a date tuple (year, month, day) to an Excel date.
# @param year Gregorian year.
# @param month 1 <= month <= 12
# @param day 1 <= day <= last day of that (year, month)
# @param datemode 0: 1900-based, 1: 1904-based.
# @throws XLDateAmbiguous The 1900 leap-year problem (datemode == 0 and 1.0 <= xldate < 61.0)
# @throws XLDateBadDatemode datemode arg is neither 0 nor 1
# @throws XLDateBadTuple (year, month, day) is too early/late or has invalid component(s)
# @throws XLDateError Covers the specific errors

def xldate_from_date_tuple(date_tuple, datemode):
    """Create an excel date from a tuple of (year, month, day)"""
    year, month, day = date_tuple

    if datemode not in (0, 1):
        raise XLDateBadDatemode(datemode)

    if year == 0 and month == 0 and day == 0:
        return 0.00

    if not (1900 <= year <= 9999):
        raise XLDateBadTuple("Invalid year: %r" % ((year, month, day),))
    if not (1 <= month <= 12):
        raise XLDateBadTuple("Invalid month: %r" % ((year, month, day),))
    if  day < 1 \
    or (day > _days_in_month[month] and not(day == 29 and month == 2 and _leap(year))):
        raise XLDateBadTuple("Invalid day: %r" % ((year, month, day),))

    Yp = year + 4716
    M = month
    if M <= 2:
        Yp = Yp - 1
        Mp = M + 9
    else:
        Mp = M - 3
    jdn = (1461 * Yp // 4) + ((979 * Mp + 16) // 32) + \
        day - 1364 - (((Yp + 184) // 100) * 3 // 4)
    xldays = jdn - _JDN_delta[datemode]
    if xldays <= 0:
        raise XLDateBadTuple("Invalid (year, month, day): %r" % ((year, month, day),))
    if xldays < 61 and datemode == 0:
        raise XLDateAmbiguous("Before 1900-03-01: %r" % ((year, month, day),))
    return float(xldays)

##
# Convert a time tuple (hour, minute, second) to an Excel "date" value (fraction of a day).
# @param hour 0 <= hour < 24
# @param minute 0 <= minute < 60
# @param second 0 <= second < 60
# @throws XLDateBadTuple Out-of-range hour, minute, or second

def xldate_from_time_tuple(time_tuple):
    """Create an excel date from a tuple of (hour, minute, second)"""
    hour, minute, second = time_tuple
    if 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60:
        return ((second / 60.0 + minute) / 60.0 + hour) / 24.0
    raise XLDateBadTuple("Invalid (hour, minute, second): %r" % ((hour, minute, second),))

##
# Convert a datetime tuple (year, month, day, hour, minute, second) to an Excel date value.
# For more details, refer to other xldate_from_*_tuple functions.
# @param datetime_tuple (year, month, day, hour, minute, second)
# @param datemode 0: 1900-based, 1: 1904-based.

def xldate_from_datetime_tuple(datetime_tuple, datemode):
    return (
        xldate_from_date_tuple(datetime_tuple[:3], datemode)
        +
        xldate_from_time_tuple(datetime_tuple[3:])
        )
