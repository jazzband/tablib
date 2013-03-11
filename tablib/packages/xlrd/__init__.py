from os import path

from .info import __VERSION__

# <p>Copyright (c) 2005-2012 Stephen John Machin, Lingfo Pty Ltd</p>
# <p>This module is part of the xlrd package, which is released under a
# BSD-style licence.</p>

from . import licences

##
# <p><b>A Python module for extracting data from MS Excel (TM) spreadsheet files.
# <br /><br />
# Version 0.7.4 -- April 2012
# </b></p>
#
# <h2>General information</h2>
#
# <h3>Acknowledgements</h3>
#
# <p>
# Development of this module would not have been possible without the document
# "OpenOffice.org's Documentation of the Microsoft Excel File Format"
# ("OOo docs" for short).
# The latest version is available from OpenOffice.org in
# <a href=http://sc.openoffice.org/excelfileformat.pdf> PDF format</a>
# and
# <a href=http://sc.openoffice.org/excelfileformat.odt> ODT format.</a>
# Small portions of the OOo docs are reproduced in this
# document. A study of the OOo docs is recommended for those who wish a
# deeper understanding of the Excel file layout than the xlrd docs can provide.
# </p>
#
# <p>Backporting to Python 2.1 was partially funded by
#   <a href=http://journyx.com/>
#       Journyx - provider of timesheet and project accounting solutions.
#   </a>
# </p>
#
# <p>Provision of formatting information in version 0.6.1 was funded by
#   <a href=http://www.simplistix.co.uk>
#       Simplistix Ltd.
#   </a>
# </p>
#
# <h3>Unicode</h3>
#
# <p>This module presents all text strings as Python unicode objects.
# From Excel 97 onwards, text in Excel spreadsheets has been stored as Unicode.
# Older files (Excel 95 and earlier) don't keep strings in Unicode;
# a CODEPAGE record provides a codepage number (for example, 1252) which is
# used by xlrd to derive the encoding (for same example: "cp1252") which is
# used to translate to Unicode.</p>
# <small>
# <p>If the CODEPAGE record is missing (possible if the file was created
# by third-party software), xlrd will assume that the encoding is ascii, and keep going.
# If the actual encoding is not ascii, a UnicodeDecodeError exception will be raised and
# you will need to determine the encoding yourself, and tell xlrd:
# <pre>
#     book = xlrd.open_workbook(..., encoding_override="cp1252")
# </pre></p>
# <p>If the CODEPAGE record exists but is wrong (for example, the codepage
# number is 1251, but the strings are actually encoded in koi8_r),
# it can be overridden using the same mechanism.
# The supplied runxlrd.py has a corresponding command-line argument, which
# may be used for experimentation:
# <pre>
#     runxlrd.py -e koi8_r 3rows myfile.xls
# </pre></p>
# <p>The first place to look for an encoding ("codec name") is
# <a href=http://docs.python.org/lib/standard-encodings.html>
# the Python documentation</a>.
# </p>
# </small>
#
# <h3>Dates in Excel spreadsheets</h3>
#
# <p>In reality, there are no such things. What you have are floating point
# numbers and pious hope.
# There are several problems with Excel dates:</p>
#
# <p>(1) Dates are not stored as a separate data type; they are stored as
# floating point numbers and you have to rely on
# (a) the "number format" applied to them in Excel and/or
# (b) knowing which cells are supposed to have dates in them.
# This module helps with (a) by inspecting the
# format that has been applied to each number cell;
# if it appears to be a date format, the cell
# is classified as a date rather than a number. Feedback on this feature,
# especially from non-English-speaking locales, would be appreciated.</p>
#
# <p>(2) Excel for Windows stores dates by default as the number of
# days (or fraction thereof) since 1899-12-31T00:00:00. Excel for
# Macintosh uses a default start date of 1904-01-01T00:00:00. The date
# system can be changed in Excel on a per-workbook basis (for example:
# Tools -> Options -> Calculation, tick the "1904 date system" box).
# This is of course a bad idea if there are already dates in the
# workbook. There is no good reason to change it even if there are no
# dates in the workbook. Which date system is in use is recorded in the
# workbook. A workbook transported from Windows to Macintosh (or vice
# versa) will work correctly with the host Excel. When using this
# module's xldate_as_tuple function to convert numbers from a workbook,
# you must use the datemode attribute of the Book object. If you guess,
# or make a judgement depending on where you believe the workbook was
# created, you run the risk of being 1462 days out of kilter.</p>
#
# <p>Reference:
# http://support.microsoft.com/default.aspx?scid=KB;EN-US;q180162</p>
#
#
# <p>(3) The Excel implementation of the Windows-default 1900-based date system works on the
# incorrect premise that 1900 was a leap year. It interprets the number 60 as meaning 1900-02-29,
# which is not a valid date. Consequently any number less than 61 is ambiguous. Example: is 59 the
# result of 1900-02-28 entered directly, or is it 1900-03-01 minus 2 days? The OpenOffice.org Calc
# program "corrects" the Microsoft problem; entering 1900-02-27 causes the number 59 to be stored.
# Save as an XLS file, then open the file with Excel -- you'll see 1900-02-28 displayed.</p>
#
# <p>Reference: http://support.microsoft.com/default.aspx?scid=kb;en-us;214326</p>
#
# <p>(4) The Macintosh-default 1904-based date system counts 1904-01-02 as day 1 and 1904-01-01 as day zero.
# Thus any number such that (0.0 <= number < 1.0) is ambiguous. Is 0.625 a time of day (15:00:00),
# independent of the calendar,
# or should it be interpreted as an instant on a particular day (1904-01-01T15:00:00)?
# The xldate_* functions in this module
# take the view that such a number is a calendar-independent time of day (like Python's datetime.time type) for both
# date systems. This is consistent with more recent Microsoft documentation
# (for example, the help file for Excel 2002 which says that the first day
# in the 1904 date system is 1904-01-02).
#
# <p>(5) Usage of the Excel DATE() function may leave strange dates in a spreadsheet. Quoting the help file,
# in respect of the 1900 date system: "If year is between 0 (zero) and 1899 (inclusive),
# Excel adds that value to 1900 to calculate the year. For example, DATE(108,1,2) returns January 2, 2008 (1900+108)."
# This gimmick, semi-defensible only for arguments up to 99 and only in the pre-Y2K-awareness era,
# means that DATE(1899, 12, 31) is interpreted as 3799-12-31.</p>
#
# <p>For further information, please refer to the documentation for the xldate_* functions.</p>
#
# <h3> Named references, constants, formulas, and macros</h3>
#
# <p>
# A name is used to refer to a cell, a group of cells, a constant
# value, a formula, or a macro. Usually the scope of a name is global
# across the whole workbook. However it can be local to a worksheet.
# For example, if the sales figures are in different cells in
# different sheets, the user may define the name "Sales" in each
# sheet. There are built-in names, like "Print_Area" and
# "Print_Titles"; these two are naturally local to a sheet.
# </p><p>
# To inspect the names with a user interface like MS Excel, OOo Calc,
# or Gnumeric, click on Insert/Names/Define. This will show the global
# names, plus those local to the currently selected sheet.
# </p><p>
# A Book object provides two dictionaries (name_map and
# name_and_scope_map) and a list (name_obj_list) which allow various
# ways of accessing the Name objects. There is one Name object for
# each NAME record found in the workbook. Name objects have many
# attributes, several of which are relevant only when obj.macro is 1.
# </p><p>
# In the examples directory you will find namesdemo.xls which
# showcases the many different ways that names can be used, and
# xlrdnamesAPIdemo.py which offers 3 different queries for inspecting
# the names in your files, and shows how to extract whatever a name is
# referring to. There is currently one "convenience method",
# Name.cell(), which extracts the value in the case where the name
# refers to a single cell. More convenience methods are planned. The
# source code for Name.cell (in __init__.py) is an extra source of
# information on how the Name attributes hang together.
# </p>
#
# <p><i>Name information is <b>not</b> extracted from files older than
# Excel 5.0 (Book.biff_version < 50)</i></p>
#
# <h3>Formatting</h3>
#
# <h4>Introduction</h4>
#
# <p>This collection of features, new in xlrd version 0.6.1, is intended
# to provide the information needed to (1) display/render spreadsheet contents
# (say) on a screen or in a PDF file, and (2) copy spreadsheet data to another
# file without losing the ability to display/render it.</p>
#
# <h4>The Palette; Colour Indexes</h4>
#
# <p>A colour is represented in Excel as a (red, green, blue) ("RGB") tuple
# with each component in range(256). However it is not possible to access an
# unlimited number of colours; each spreadsheet is limited to a palette of 64 different
# colours (24 in Excel 3.0 and 4.0, 8 in Excel 2.0). Colours are referenced by an index
# ("colour index") into this palette.
#
# Colour indexes 0 to 7 represent 8 fixed built-in colours: black, white, red, green, blue,
# yellow, magenta, and cyan.<p>
#
# The remaining colours in the palette (8 to 63 in Excel 5.0 and later)
# can be changed by the user. In the Excel 2003 UI, Tools/Options/Color presents a palette
# of 7 rows of 8 colours. The last two rows are reserved for use in charts.<br />
# The correspondence between this grid and the assigned
# colour indexes is NOT left-to-right top-to-bottom.<br />
# Indexes 8 to 15 correspond to changeable
# parallels of the 8 fixed colours -- for example, index 7 is forever cyan;
# index 15 starts off being cyan but can be changed by the user.<br />
#
# The default colour for each index depends on the file version; tables of the defaults
# are available in the source code. If the user changes one or more colours,
# a PALETTE record appears in the XLS file -- it gives the RGB values for *all* changeable
# indexes.<br />
# Note that colours can be used in "number formats": "[CYAN]...." and "[COLOR8]...." refer
# to colour index 7; "[COLOR16]...." will produce cyan
# unless the user changes colour index 15 to something else.<br />
#
# <p>In addition, there are several "magic" colour indexes used by Excel:<br />
# 0x18 (BIFF3-BIFF4), 0x40 (BIFF5-BIFF8): System window text colour for border lines
# (used in XF, CF, and WINDOW2 records)<br />
# 0x19 (BIFF3-BIFF4), 0x41 (BIFF5-BIFF8): System window background colour for pattern background
# (used in XF and CF records )<br />
# 0x43: System face colour (dialogue background colour)<br />
# 0x4D: System window text colour for chart border lines<br />
# 0x4E: System window background colour for chart areas<br />
# 0x4F: Automatic colour for chart border lines (seems to be always Black)<br />
# 0x50: System ToolTip background colour (used in note objects)<br />
# 0x51: System ToolTip text colour (used in note objects)<br />
# 0x7FFF: System window text colour for fonts (used in FONT and CF records)<br />
# Note 0x7FFF appears to be the *default* colour index. It appears quite often in FONT
# records.<br />
#
# <h4>Default Formatting</h4>
#
# Default formatting is applied to all empty cells (those not described by a cell record).
# Firstly row default information (ROW record, Rowinfo class) is used if available.
# Failing that, column default information (COLINFO record, Colinfo class) is used if available.
# As a last resort the worksheet/workbook default cell format will be used; this
# should always be present in an Excel file,
# described by the XF record with the fixed index 15 (0-based). By default, it uses the
# worksheet/workbook default cell style, described by the very first XF record (index 0).
#
# <h4> Formatting features not included in xlrd version 0.6.1</h4>
# <ul>
#   <li>Rich text i.e. strings containing partial <b>bold</b> <i>italic</i>
#       and <u>underlined</u> text, change of font inside a string, etc.
#       See OOo docs s3.4 and s3.2.
#       <i> Rich text is included in version 0.7.2</i></li>
#   <li>Asian phonetic text (known as "ruby"), used for Japanese furigana. See OOo docs
#       s3.4.2 (p15)</li>
#   <li>Conditional formatting. See OOo docs
#       s5.12, s6.21 (CONDFMT record), s6.16 (CF record)</li>
#   <li>Miscellaneous sheet-level and book-level items e.g. printing layout, screen panes. </li>
#   <li>Modern Excel file versions don't keep most of the built-in
#       "number formats" in the file; Excel loads formats according to the
#       user's locale. Currently xlrd's emulation of this is limited to
#       a hard-wired table that applies to the US English locale. This may mean
#       that currency symbols, date order, thousands separator, decimals separator, etc
#       are inappropriate. Note that this does not affect users who are copying XLS
#       files, only those who are visually rendering cells.</li>
# </ul>
#
# <h3>Loading worksheets on demand</h3>
#
# <p>This feature, new in version 0.7.1, is governed by the on_demand argument
# to the open_workbook() function and allows saving memory and time by loading
# only those sheets that the caller is interested in, and releasing sheets
# when no longer required.</p>
#
# <p>on_demand=False (default): No change. open_workbook() loads global data
# and all sheets, releases resources no longer required (principally the
# str or mmap object containing the Workbook stream), and returns.</p>
#
# <p>on_demand=True and BIFF version < 5.0: A warning message is emitted,
# on_demand is recorded as False, and the old process is followed.</p>
#
# <p>on_demand=True and BIFF version >= 5.0: open_workbook() loads global
# data and returns without releasing resources. At this stage, the only
# information available about sheets is Book.nsheets and Book.sheet_names().</p>
#
# <p>Book.sheet_by_name() and Book.sheet_by_index() will load the requested
# sheet if it is not already loaded.</p>
#
# <p>Book.sheets() will load all/any unloaded sheets.</p>
#
# <p>The caller may save memory by calling
# Book.unload_sheet(sheet_name_or_index) when finished with the sheet.
# This applies irrespective of the state of on_demand.</p>
#
# <p>The caller may re-load an unloaded sheet by calling Book.sheet_by_xxxx()
#  -- except if those required resources have been released (which will
# have happened automatically when on_demand is false). This is the only
# case where an exception will be raised.</p>
#
# <p>The caller may query the state of a sheet:
# Book.sheet_loaded(sheet_name_or_index) -> a bool</p>
#
# <p> Book.release_resources() may used to save memory and close
# any memory-mapped file before proceding to examine already-loaded
# sheets. Once resources are released, no further sheets can be loaded.</p>
#
# <p> When using on-demand, it is advisable to ensure that
# Book.release_resources() is always called even if an exception
# is raised in your own code; otherwise if the input file has been
# memory-mapped, the mmap.mmap object will not be closed and you will
# not be able to access the physical file until your Python process
# terminates. This can be done by calling Book.release_resources()
# explicitly in the finally suite of a try/finally block.
# New in xlrd 0.7.2: the Book object is a "context manager", so if
# using Python 2.5 or later, you can wrap your code in a "with"
# statement.</p>
##

import sys, zipfile, pprint
from . import timemachine
from .biffh import (
    XLRDError,
    biff_text_from_num,
    error_text_from_code,
    XL_CELL_BLANK,
    XL_CELL_TEXT,
    XL_CELL_BOOLEAN,
    XL_CELL_ERROR,
    XL_CELL_EMPTY,
    XL_CELL_DATE,
    XL_CELL_NUMBER
    )
from .formula import * # is constrained by __all__
from .book import Book, colname #### TODO #### formula also has `colname` (restricted to 256 cols)
from .sheet import empty_cell
from .xldate import XLDateError, xldate_as_tuple

if sys.version.startswith("IronPython"):
    # print >> sys.stderr, "...importing encodings"
    import encodings

try:
    import mmap
    MMAP_AVAILABLE = 1
except ImportError:
    MMAP_AVAILABLE = 0
USE_MMAP = MMAP_AVAILABLE

##
#
# Open a spreadsheet file for data extraction.
#
# @param filename The path to the spreadsheet file to be opened.
#
# @param logfile An open file to which messages and diagnostics are written.
#
# @param verbosity Increases the volume of trace material written to the logfile.
#
# @param pickleable Default is true. In Python 2.4 or earlier, setting to false
# will cause use of array.array objects which save some memory but can't be pickled.
# In Python 2.5, array.arrays are used unconditionally. Note: if you have large files that
# you need to read multiple times, it can be much faster to cPickle.dump() the xlrd.Book object
# once, and use cPickle.load() multiple times.
# @param use_mmap Whether to use the mmap module is determined heuristically.
# Use this arg to override the result. Current heuristic: mmap is used if it exists.
#
# @param file_contents ... as a string or an mmap.mmap object or some other behave-alike object.
# If file_contents is supplied, filename will not be used, except (possibly) in messages.
#
# @param encoding_override Used to overcome missing or bad codepage information
# in older-version files. Refer to discussion in the <b>Unicode</b> section above.
# <br /> -- New in version 0.6.0
#
# @param formatting_info Governs provision of a reference to an XF (eXtended Format) object
# for each cell in the worksheet.
# <br /> Default is <i>False</i>. This is backwards compatible and saves memory.
# "Blank" cells (those with their own formatting information but no data) are treated as empty
# (by ignoring the file's BLANK and MULBLANK records).
# It cuts off any bottom "margin" of rows of empty (and blank) cells and
# any right "margin" of columns of empty (and blank) cells.
# Only cell_value and cell_type are available.
# <br /> <i>True</i> provides all cells, including empty and blank cells.
# XF information is available for each cell.
# <br /> -- New in version 0.6.1
#
# @param on_demand Governs whether sheets are all loaded initially or when demanded
# by the caller. Please refer back to the section "Loading worksheets on demand" for details.
# <br /> -- New in version 0.7.1
#
# @param ragged_rows False (the default) means all rows are padded out with empty cells so that all
# rows have the same size (Sheet.ncols). True means that there are no empty cells at the ends of rows.
# This can result in substantial memory savings if rows are of widely varying sizes. See also the
# Sheet.row_len() method.
# <br /> -- New in version 0.7.2
#
# @return An instance of the Book class.

def open_workbook(filename=None,
    logfile=sys.stdout,
    verbosity=0,
    pickleable=True,
    use_mmap=USE_MMAP,
    file_contents=None,
    encoding_override=None,
    formatting_info=False,
    on_demand=False,
    ragged_rows=False,
    ):
    peeksz = 4
    if file_contents:
        peek = file_contents[:peeksz]
    else:
        f = open(filename, "rb")
        peek = f.read(peeksz)
        f.close()
    if peek == b"PK\x03\x04": # a ZIP file
        if file_contents:
            zf = zipfile.ZipFile(timemachine.BYTES_IO(file_contents))
        else:
            zf = zipfile.ZipFile(filename)
        component_names = zf.namelist()
        if verbosity:
            logfile.write('ZIP component_names:\n')
            pprint.pprint(component_names, logfile)
        if 'xl/workbook.xml' in component_names:
            from . import xlsx
            bk = xlsx.open_workbook_2007_xml(
                zf,
                component_names,
                logfile=logfile,
                verbosity=verbosity,
                pickleable=pickleable,
                use_mmap=mmap,
                formatting_info=formatting_info,
                on_demand=on_demand,
                ragged_rows=ragged_rows,
                )
            return bk
        if 'xl/workbook.bin' in component_names:
            raise XLRDError('Excel 2007 xlsb file; not supported')
        if 'content.xml' in component_names:
            raise XLRDError('Openoffice.org ODS file; not supported')
        raise XLRDError('ZIP file contents not a known type of workbook')

    from . import book
    bk = book.open_workbook_xls(
        filename=filename,
        logfile=logfile,
        verbosity=verbosity,
        pickleable=pickleable,
        use_mmap=use_mmap,
        file_contents=file_contents,
        encoding_override=encoding_override,
        formatting_info=formatting_info,
        on_demand=on_demand,
        ragged_rows=ragged_rows,
        )
    return bk

##
# For debugging: dump an XLS file's BIFF records in char & hex.
# @param filename The path to the file to be dumped.
# @param outfile An open file, to which the dump is written.
# @param unnumbered If true, omit offsets (for meaningful diffs).

def dump(filename, outfile=sys.stdout, unnumbered=False):
    from .book import Book
    from .biffh import biff_dump
    bk = Book()
    bk.biff2_8_load(filename=filename, logfile=outfile, )
    biff_dump(bk.mem, bk.base, bk.stream_len, 0, outfile, unnumbered)

##
# For debugging and analysis: summarise the file's BIFF records.
# I.e. produce a sorted file of (record_name, count).
# @param filename The path to the file to be summarised.
# @param outfile An open file, to which the summary is written.

def count_records(filename, outfile=sys.stdout):
    from .book import Book
    from .biffh import biff_count_records
    bk = Book()
    bk.biff2_8_load(filename=filename, logfile=outfile, )
    biff_count_records(bk.mem, bk.base, bk.stream_len, outfile)
