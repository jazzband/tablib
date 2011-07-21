# -*- coding: cp1252 -*-

__VERSION__ = "0.7.1" # 2009-05-31

# <p>Copyright © 2005-2009 Stephen John Machin, Lingfo Pty Ltd</p>
# <p>This module is part of the xlrd package, which is released under a
# BSD-style licence.</p>

import licences

##
# <p><b>A Python module for extracting data from MS Excel ™ spreadsheet files.
# <br /><br />
# Version 0.7.1 -- 2009-05-31
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
#       See OOo docs s3.4 and s3.2</li>
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
##

# 2009-04-27 SJM Integrated on_demand patch by Armando Serrano Lombillo
# 2008-11-23 SJM Support dumping FILEPASS and EXTERNNAME records; extra info from SUPBOOK records
# 2008-11-23 SJM colname utility function now supports more than 256 columns
# 2008-04-24 SJM Recovery code for file with out-of-order/missing/wrong CODEPAGE record needed to be called for EXTERNSHEET/BOUNDSHEET/NAME/SHEETHDR records.
# 2008-02-08 SJM Preparation for Excel 2.0 support
# 2008-02-03 SJM Minor tweaks for IronPython support
# 2008-02-02 SJM Previous change stopped dump() and count_records() ... fixed
# 2007-12-25 SJM Decouple Book initialisation & loading -- to allow for multiple loaders.
# 2007-12-20 SJM Better error message for unsupported file format.
# 2007-12-04 SJM Added support for Excel 2.x (BIFF2) files.
# 2007-11-20 SJM Wasn't handling EXTERNSHEET record that needed CONTINUE record(s)
# 2007-07-07 SJM Version changed to 0.7.0 (alpha 1)
# 2007-07-07 SJM Logfile arg wasn't being passed from open_workbook to compdoc.CompDoc
# 2007-05-21 SJM If no CODEPAGE record in pre-8.0 file, assume ascii and keep going.
# 2007-04-22 SJM Removed antique undocumented Book.get_name_dict method.

from timemachine import *
from biffh import *
from struct import unpack
import sys
import time
import sheet
import compdoc
from xldate import xldate_as_tuple, XLDateError
from formula import *
import formatting
if sys.version.startswith("IronPython"):
    # print >> sys.stderr, "...importing encodings"
    import encodings

empty_cell = sheet.empty_cell # for exposure to the world ...

DEBUG = 0

USE_FANCY_CD = 1

TOGGLE_GC = 0
import gc
# gc.set_debug(gc.DEBUG_STATS)

try:
    import mmap
    MMAP_AVAILABLE = 1
except ImportError:
    MMAP_AVAILABLE = 0
USE_MMAP = MMAP_AVAILABLE

MY_EOF = 0xF00BAAA # not a 16-bit number

SUPBOOK_UNK, SUPBOOK_INTERNAL, SUPBOOK_EXTERNAL, SUPBOOK_ADDIN, SUPBOOK_DDEOLE = range(5)

SUPPORTED_VERSIONS = (80, 70, 50, 45, 40, 30, 21, 20)

code_from_builtin_name = {
    u"Consolidate_Area": u"\x00",
    u"Auto_Open":        u"\x01",
    u"Auto_Close":       u"\x02",
    u"Extract":          u"\x03",
    u"Database":         u"\x04",
    u"Criteria":         u"\x05",
    u"Print_Area":       u"\x06",
    u"Print_Titles":     u"\x07",
    u"Recorder":         u"\x08",
    u"Data_Form":        u"\x09",
    u"Auto_Activate":    u"\x0A",
    u"Auto_Deactivate":  u"\x0B",
    u"Sheet_Title":      u"\x0C",
    u"_FilterDatabase":  u"\x0D",
    }
builtin_name_from_code = {}
for _bin, _bic in code_from_builtin_name.items():
    builtin_name_from_code[_bic] = _bin
del _bin, _bic

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
# -- New in version 0.7.1
#
# @return An instance of the Book class.

def open_workbook(filename=None,
    logfile=sys.stdout, verbosity=0, pickleable=True, use_mmap=USE_MMAP,
    file_contents=None,
    encoding_override=None,
    formatting_info=False, on_demand=False,
    ):
    t0 = time.clock()
    if TOGGLE_GC:
        orig_gc_enabled = gc.isenabled()
        if orig_gc_enabled:
            gc.disable()
    bk = Book()
    bk.biff2_8_load(
        filename=filename, file_contents=file_contents,
        logfile=logfile, verbosity=verbosity, pickleable=pickleable, use_mmap=use_mmap,
        encoding_override=encoding_override,
        formatting_info=formatting_info,
        on_demand=on_demand,
        )
    t1 = time.clock()
    bk.load_time_stage_1 = t1 - t0
    biff_version = bk.getbof(XL_WORKBOOK_GLOBALS)
    if not biff_version:
        raise XLRDError("Can't determine file's BIFF version")
    if biff_version not in SUPPORTED_VERSIONS:
        raise XLRDError(
            "BIFF version %s is not supported"
            % biff_text_from_num[biff_version]
            )
    bk.biff_version = biff_version
    if biff_version <= 40:
        # no workbook globals, only 1 worksheet
        if on_demand:
            fprintf(bk.logfile,
                "*** WARNING: on_demand is not supported for this Excel version.\n"
                "*** Setting on_demand to False.\n")
            bk.on_demand = on_demand = False
        bk.fake_globals_get_sheet()
    elif biff_version == 45:
        # worksheet(s) embedded in global stream
        bk.parse_globals()
        if on_demand:
            fprintf(bk.logfile, "*** WARNING: on_demand is not supported for this Excel version.\n"
                                "*** Setting on_demand to False.\n")
            bk.on_demand = on_demand = False
    else:
        bk.parse_globals()
        bk._sheet_list = [None for sh in bk._sheet_names]
        if not on_demand:
            bk.get_sheets()
    bk.nsheets = len(bk._sheet_list)
    if biff_version == 45 and bk.nsheets > 1:
        fprintf(bk.logfile,
            "*** WARNING: Excel 4.0 workbook (.XLW) file contains %d worksheets.\n"
            "*** Book-level data will be that of the last worksheet.\n",
            bk.nsheets
            )
    if not on_demand:
        bk.release_resources()
    if TOGGLE_GC:
        if orig_gc_enabled:
            gc.enable()
    t2 = time.clock()
    bk.load_time_stage_2 = t2 - t1
    return bk

##
# For debugging: dump the file's BIFF records in char & hex.
# @param filename The path to the file to be dumped.
# @param outfile An open file, to which the dump is written.
# @param unnumbered If true, omit offsets (for meaningful diffs).

def dump(filename, outfile=sys.stdout, unnumbered=False):
    bk = Book()
    bk.biff2_8_load(filename=filename, logfile=outfile, )
    biff_dump(bk.mem, bk.base, bk.stream_len, 0, outfile, unnumbered)

##
# For debugging and analysis: summarise the file's BIFF records.
# I.e. produce a sorted file of (record_name, count).
# @param filename The path to the file to be summarised.
# @param outfile An open file, to which the summary is written.

def count_records(filename, outfile=sys.stdout):
    bk = Book()
    bk.biff2_8_load(filename=filename, logfile=outfile, )
    biff_count_records(bk.mem, bk.base, bk.stream_len, outfile)

##
# Information relating to a named reference, formula, macro, etc.
# <br />  -- New in version 0.6.0
# <br />  -- <i>Name information is <b>not</b> extracted from files older than
# Excel 5.0 (Book.biff_version < 50)</i>

class Name(BaseObject):

    _repr_these = ['stack']
    book = None # parent

    ##
    # 0 = Visible; 1 = Hidden
    hidden = 0

    ##
    # 0 = Command macro; 1 = Function macro. Relevant only if macro == 1
    func = 0

    ##
    # 0 = Sheet macro; 1 = VisualBasic macro. Relevant only if macro == 1
    vbasic = 0

    ##
    # 0 = Standard name; 1 = Macro name
    macro = 0

    ##
    # 0 = Simple formula; 1 = Complex formula (array formula or user defined)<br />
    # <i>No examples have been sighted.</i>
    complex = 0

    ##
    # 0 = User-defined name; 1 = Built-in name
    # (common examples: Print_Area, Print_Titles; see OOo docs for full list)
    builtin = 0

    ##
    # Function group. Relevant only if macro == 1; see OOo docs for values.
    funcgroup = 0

    ##
    # 0 = Formula definition; 1 = Binary data<br />  <i>No examples have been sighted.</i>
    binary = 0

    ##
    # The index of this object in book.name_obj_list
    name_index = 0

    ##
    # A Unicode string. If builtin, decoded as per OOo docs.
    name = u""

    ##
    # An 8-bit string.
    raw_formula = ""

    ##
    # -1: The name is global (visible in all calculation sheets).<br />
    # -2: The name belongs to a macro sheet or VBA sheet.<br />
    # -3: The name is invalid.<br />
    # 0 <= scope < book.nsheets: The name is local to the sheet whose index is scope.
    scope = -1

    ##
    # The result of evaluating the formula, if any.
    # If no formula, or evaluation of the formula encountered problems,
    # the result is None. Otherwise the result is a single instance of the
    # Operand class.
    #
    result = None

    ##
    # This is a convenience method for the frequent use case where the name
    # refers to a single cell.
    # @return An instance of the Cell class.
    # @throws XLRDError The name is not a constant absolute reference
    # to a single cell.
    def cell(self):
        res = self.result
        if res:
            # result should be an instance of the Operand class
            kind = res.kind
            value = res.value
            if kind == oREF and len(value) == 1:
                ref3d = value[0]
                if (0 <= ref3d.shtxlo == ref3d.shtxhi - 1
                and      ref3d.rowxlo == ref3d.rowxhi - 1
                and      ref3d.colxlo == ref3d.colxhi - 1):
                    sh = self.book.sheet_by_index(ref3d.shtxlo)
                    return sh.cell(ref3d.rowxlo, ref3d.colxlo)
        self.dump(self.book.logfile,
            header="=== Dump of Name object ===",
            footer="======= End of dump =======",
            )
        raise XLRDError("Not a constant absolute reference to a single cell")

    ##
    # This is a convenience method for the use case where the name
    # refers to one rectangular area in one worksheet.
    # @param clipped If true (the default), the returned rectangle is clipped
    # to fit in (0, sheet.nrows, 0, sheet.ncols) -- it is guaranteed that
    # 0 <= rowxlo <= rowxhi <= sheet.nrows and that the number of usable rows
    # in the area (which may be zero) is rowxhi - rowxlo; likewise for columns.
    # @return a tuple (sheet_object, rowxlo, rowxhi, colxlo, colxhi).
    # @throws XLRDError The name is not a constant absolute reference
    # to a single area in a single sheet.
    def area2d(self, clipped=True):
        res = self.result
        if res:
            # result should be an instance of the Operand class
            kind = res.kind
            value = res.value
            if kind == oREF and len(value) == 1: # only 1 reference
                ref3d = value[0]
                if 0 <= ref3d.shtxlo == ref3d.shtxhi - 1: # only 1 usable sheet
                    sh = self.book.sheet_by_index(ref3d.shtxlo)
                    if not clipped:
                        return sh, ref3d.rowxlo, ref3d.rowxhi, ref3d.colxlo, ref3d.colxhi
                    rowxlo = min(ref3d.rowxlo, sh.nrows)
                    rowxhi = max(rowxlo, min(ref3d.rowxhi, sh.nrows))
                    colxlo = min(ref3d.colxlo, sh.ncols)
                    colxhi = max(colxlo, min(ref3d.colxhi, sh.ncols))
                    assert 0 <= rowxlo <= rowxhi <= sh.nrows
                    assert 0 <= colxlo <= colxhi <= sh.ncols
                    return sh, rowxlo, rowxhi, colxlo, colxhi
        self.dump(self.book.logfile,
            header="=== Dump of Name object ===",
            footer="======= End of dump =======",
            )
        raise XLRDError("Not a constant absolute reference to a single area in a single sheet")

##
# Contents of a "workbook".
# <p>WARNING: You don't call this class yourself. You use the Book object that
# was returned when you called xlrd.open_workbook("myfile.xls").</p>

class Book(BaseObject):

    ##
    # The number of worksheets present in the workbook file.
    # This information is available even when no sheets have yet been loaded.
    nsheets = 0

    ##
    # Which date system was in force when this file was last saved.<br />
    #    0 => 1900 system (the Excel for Windows default).<br />
    #    1 => 1904 system (the Excel for Macintosh default).<br />
    datemode = 0 # In case it's not specified in the file.

    ##
    # Version of BIFF (Binary Interchange File Format) used to create the file.
    # Latest is 8.0 (represented here as 80), introduced with Excel 97.
    # Earliest supported by this module: 2.0 (represented as 20).
    biff_version = 0

    ##
    # List containing a Name object for each NAME record in the workbook.
    # <br />  -- New in version 0.6.0
    name_obj_list = []

    ##
    # An integer denoting the character set used for strings in this file.
    # For BIFF 8 and later, this will be 1200, meaning Unicode; more precisely, UTF_16_LE.
    # For earlier versions, this is used to derive the appropriate Python encoding
    # to be used to convert to Unicode.
    # Examples: 1252 -> 'cp1252', 10000 -> 'mac_roman'
    codepage = None

    ##
    # The encoding that was derived from the codepage.
    encoding = None

    ##
    # A tuple containing the (telephone system) country code for:<br />
    #    [0]: the user-interface setting when the file was created.<br />
    #    [1]: the regional settings.<br />
    # Example: (1, 61) meaning (USA, Australia).
    # This information may give a clue to the correct encoding for an unknown codepage.
    # For a long list of observed values, refer to the OpenOffice.org documentation for
    # the COUNTRY record.
    countries = (0, 0)

    ##
    # What (if anything) is recorded as the name of the last user to save the file.
    user_name = u''

    ##
    # A list of Font class instances, each corresponding to a FONT record.
    # <br /> -- New in version 0.6.1
    font_list = []

    ##
    # A list of XF class instances, each corresponding to an XF record.
    # <br /> -- New in version 0.6.1
    xf_list = []

    ##
    # A list of Format objects, each corresponding to a FORMAT record, in
    # the order that they appear in the input file.
    # It does <i>not</i> contain builtin formats.
    # If you are creating an output file using (for example) pyExcelerator,
    # use this list.
    # The collection to be used for all visual rendering purposes is format_map.
    # <br /> -- New in version 0.6.1
    format_list = []

    ##
    # The mapping from XF.format_key to Format object.
    # <br /> -- New in version 0.6.1
    format_map = {}

    ##
    # This provides access via name to the extended format information for
    # both built-in styles and user-defined styles.<br />
    # It maps <i>name</i> to (<i>built_in</i>, <i>xf_index</i>), where:<br />
    # <i>name</i> is either the name of a user-defined style,
    # or the name of one of the built-in styles. Known built-in names are
    # Normal, RowLevel_1 to RowLevel_7,
    # ColLevel_1 to ColLevel_7, Comma, Currency, Percent, "Comma [0]",
    # "Currency [0]", Hyperlink, and "Followed Hyperlink".<br />
    # <i>built_in</i> 1 = built-in style, 0 = user-defined<br />
    # <i>xf_index</i> is an index into Book.xf_list.<br />
    # References: OOo docs s6.99 (STYLE record); Excel UI Format/Style
    # <br /> -- New in version 0.6.1
    style_name_map = {}

    ##
    # This provides definitions for colour indexes. Please refer to the
    # above section "The Palette; Colour Indexes" for an explanation
    # of how colours are represented in Excel.<br />
    # Colour indexes into the palette map into (red, green, blue) tuples.
    # "Magic" indexes e.g. 0x7FFF map to None.
    # <i>colour_map</i> is what you need if you want to render cells on screen or in a PDF
    # file. If you are writing an output XLS file, use <i>palette_record</i>.
    # <br /> -- New in version 0.6.1. Extracted only if open_workbook(..., formatting_info=True)
    colour_map = {}

    ##
    # If the user has changed any of the colours in the standard palette, the XLS
    # file will contain a PALETTE record with 56 (16 for Excel 4.0 and earlier)
    # RGB values in it, and this list will be e.g. [(r0, b0, g0), ..., (r55, b55, g55)].
    # Otherwise this list will be empty. This is what you need if you are
    # writing an output XLS file. If you want to render cells on screen or in a PDF
    # file, use colour_map.
    # <br /> -- New in version 0.6.1. Extracted only if open_workbook(..., formatting_info=True)
    palette_record = []

    ##
    # Time in seconds to extract the XLS image as a contiguous string (or mmap equivalent).
    load_time_stage_1 = -1.0

    ##
    # Time in seconds to parse the data from the contiguous string (or mmap equivalent).
    load_time_stage_2 = -1.0

    ##
    # @return A list of all sheets in the book.
    # All sheets not already loaded will be loaded.
    def sheets(self):
        for sheetx in xrange(self.nsheets):
            if not self._sheet_list[sheetx]:
                self.get_sheet(sheetx)
        return self._sheet_list[:]

    ##
    # @param sheetx Sheet index in range(nsheets)
    # @return An object of the Sheet class
    def sheet_by_index(self, sheetx):
        return self._sheet_list[sheetx] or self.get_sheet(sheetx)

    ##
    # @param sheet_name Name of sheet required
    # @return An object of the Sheet class
    def sheet_by_name(self, sheet_name):
        try:
            sheetx = self._sheet_names.index(sheet_name)
        except ValueError:
            raise XLRDError('No sheet named <%r>' % sheet_name)
        return self.sheet_by_index(sheetx)

    ##
    # @return A list of the names of all the worksheets in the workbook file.
    # This information is available even when no sheets have yet been loaded.
    def sheet_names(self):
        return self._sheet_names[:]

    ##
    # @param sheet_name_or_index Name or index of sheet enquired upon
    # @return true if sheet is loaded, false otherwise
    # <br />  -- New in version 0.7.1
    def sheet_loaded(self, sheet_name_or_index):
        # using type(1) because int won't work with Python 2.1
        if isinstance(sheet_name_or_index, type(1)):
            sheetx = sheet_name_or_index
        else:
            try:
                sheetx = self._sheet_names.index(sheet_name_or_index)
            except ValueError:
                raise XLRDError('No sheet named <%r>' % sheet_name_or_index)
        return self._sheet_list[sheetx] and True or False # Python 2.1 again

    ##
    # @param sheet_name_or_index Name or index of sheet to be unloaded.
    # <br />  -- New in version 0.7.1
    def unload_sheet(self, sheet_name_or_index):
        # using type(1) because int won't work with Python 2.1
        if isinstance(sheet_name_or_index, type(1)):
            sheetx = sheet_name_or_index
        else:
            try:
                sheetx = self._sheet_names.index(sheet_name_or_index)
            except ValueError:
                raise XLRDError('No sheet named <%r>' % sheet_name_or_index)
        self._sheet_list[sheetx] = None

    ##
    # A mapping from (lower_case_name, scope) to a single Name object.
    # <br />  -- New in version 0.6.0
    name_and_scope_map = {}

    ##
    # A mapping from lower_case_name to a list of Name objects. The list is
    # sorted in scope order. Typically there will be one item (of global scope)
    # in the list.
    # <br />  -- New in version 0.6.0
    name_map = {}

    def __init__(self):
        self._sheet_list = []
        self._sheet_names = []
        self._sheet_visibility = [] # from BOUNDSHEET record
        self.nsheets = 0
        self._sh_abs_posn = [] # sheet's absolute position in the stream
        self._sharedstrings = []
        self.raw_user_name = False
        self._sheethdr_count = 0 # BIFF 4W only
        self.builtinfmtcount = -1 # unknown as yet. BIFF 3, 4S, 4W
        self.initialise_format_info()
        self._all_sheets_count = 0 # includes macro & VBA sheets
        self._supbook_count = 0
        self._supbook_locals_inx = None
        self._supbook_addins_inx = None
        self._all_sheets_map = [] # maps an all_sheets index to a calc-sheets index (or -1)
        self._externsheet_info = []
        self._externsheet_type_b57 = []
        self._extnsht_name_from_num = {}
        self._sheet_num_from_name = {}
        self._extnsht_count = 0
        self._supbook_types = []
        self._resources_released = 0
        self.addin_func_names = []
        self.name_obj_list = []
        self.colour_map = {}
        self.palette_record = []
        self.xf_list = []
        self.style_name_map = {}

    def biff2_8_load(self, filename=None, file_contents=None,
        logfile=sys.stdout, verbosity=0, pickleable=True, use_mmap=USE_MMAP,
        encoding_override=None,
        formatting_info=False,
        on_demand=False,
        ):
        # DEBUG = 0
        self.logfile = logfile
        self.verbosity = verbosity
        self.pickleable = pickleable
        self.use_mmap = use_mmap and MMAP_AVAILABLE
        self.encoding_override = encoding_override
        self.formatting_info = formatting_info
        self.on_demand = on_demand

        need_close_filestr = 0
        if not file_contents:
            if python_version < (2, 2) and self.use_mmap:
                # need to open for update
                open_mode = "r+b"
            else:
                open_mode = "rb"
            retry = False
            try:
                f = open(filename, open_mode)
            except IOError:
                e, v = sys.exc_info()[:2]
                if open_mode == "r+b" \
                and (v.errno == 13 or v.strerror == "Permission denied"):
                    # Maybe the file is read-only
                    retry = True
                    self.use_mmap = False
                else:
                    raise
            if retry:
                f = open(filename, "rb")
            if self.use_mmap:
                f.seek(0, 2) # EOF
                size = f.tell()
                f.seek(0, 0) # BOF
                if python_version < (2, 2):
                    filestr = mmap.mmap(f.fileno(), size)
                else:
                    filestr = mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ)
                need_close_filestr = 1
                self.stream_len = size
            else:
                filestr = f.read()
                self.stream_len = len(filestr)
            f.close()
        else:
            filestr = file_contents
            self.stream_len = len(file_contents)

        self.base = 0
        if filestr[:8] != compdoc.SIGNATURE:
            # got this one at the antique store
            self.mem = filestr
        else:
            cd = compdoc.CompDoc(filestr, logfile=self.logfile)
            if USE_FANCY_CD:
                for qname in [u'Workbook', u'Book']:
                    self.mem, self.base, self.stream_len = cd.locate_named_stream(qname)
                    if self.mem: break
                else:
                    raise XLRDError("Can't find workbook in OLE2 compound document")
            else:
                for qname in [u'Workbook', u'Book']:
                    self.mem = cd.get_named_stream(qname)
                    if self.mem: break
                else:
                    raise XLRDError("Can't find workbook in OLE2 compound document")
                self.stream_len = len(self.mem)
            del cd
            if self.mem is not filestr:
                if need_close_filestr:
                    filestr.close()
                del filestr
        self._position = self.base
        if DEBUG:
            print >> self.logfile, "mem: %s, base: %d, len: %d" % (type(self.mem), self.base, self.stream_len)

    def initialise_format_info(self):
        # needs to be done once per sheet for BIFF 4W :-(
        self.format_map = {}
        self.format_list = []
        self.xfcount = 0
        self.actualfmtcount = 0 # number of FORMAT records seen so far
        self._xf_index_to_xl_type_map = {}
        self._xf_epilogue_done = 0
        self.xf_list = []
        self.font_list = []

    def release_resources(self):
        self._resources_released = 1
        del self.mem
        del self._sharedstrings

    def get2bytes(self):
        pos = self._position
        buff_two = self.mem[pos:pos+2]
        lenbuff = len(buff_two)
        self._position += lenbuff
        if lenbuff < 2:
            return MY_EOF
        lo, hi = buff_two
        return (ord(hi) << 8) | ord(lo)

    def get_record_parts(self):
        pos = self._position
        mem = self.mem
        code, length = unpack('<HH', mem[pos:pos+4])
        pos += 4
        data = mem[pos:pos+length]
        self._position = pos + length
        return (code, length, data)

    def get_record_parts_conditional(self, reqd_record):
        pos = self._position
        mem = self.mem
        code, length = unpack('<HH', mem[pos:pos+4])
        if code != reqd_record:
            return (None, 0, '')
        pos += 4
        data = mem[pos:pos+length]
        self._position = pos + length
        return (code, length, data)

    def get_sheet(self, sh_number, update_pos=True):
        if self._resources_released:
            raise XLRDError("Can't load sheets after releasing resources.")
        if update_pos:
            self._position = self._sh_abs_posn[sh_number]
        _unused_biff_version = self.getbof(XL_WORKSHEET)
        # assert biff_version == self.biff_version ### FAILS
        # Have an example where book is v7 but sheet reports v8!!!
        # It appears to work OK if the sheet version is ignored.
        # Confirmed by Daniel Rentz: happens when Excel does "save as"
        # creating an old version file; ignore version details on sheet BOF.
        sh = sheet.Sheet(self,
                self._position,
                self._sheet_names[sh_number],
                sh_number,
                )
        sh.read(self)
        self._sheet_list[sh_number] = sh
        return sh

    def get_sheets(self):
        # DEBUG = 0
        if DEBUG: print >> self.logfile, "GET_SHEETS:", self._sheet_names, self._sh_abs_posn
        for sheetno in xrange(len(self._sheet_names)):
            if DEBUG: print >> self.logfile, "GET_SHEETS: sheetno =", sheetno, self._sheet_names, self._sh_abs_posn
            self.get_sheet(sheetno)

    def fake_globals_get_sheet(self): # for BIFF 4.0 and earlier
        formatting.initialise_book(self)
        fake_sheet_name = u'Sheet 1'
        self._sheet_names = [fake_sheet_name]
        self._sh_abs_posn = [0]
        self._sheet_visibility = [0] # one sheet, visible
        self._sheet_list.append(None) # get_sheet updates _sheet_list but needs a None beforehand
        self.get_sheets()

    def handle_boundsheet(self, data):
        # DEBUG = 1
        bv = self.biff_version
        self.derive_encoding()
        if DEBUG:
            fprintf(self.logfile, "BOUNDSHEET: bv=%d data %r\n", bv, data);
        if bv == 45: # BIFF4W
            #### Not documented in OOo docs ...
            # In fact, the *only* data is the name of the sheet.
            sheet_name = unpack_string(data, 0, self.encoding, lenlen=1)
            visibility = 0
            sheet_type = XL_BOUNDSHEET_WORKSHEET # guess, patch later
            if len(self._sh_abs_posn) == 0:
                abs_posn = self._sheetsoffset + self.base
                # Note (a) this won't be used
                # (b) it's the position of the SHEETHDR record
                # (c) add 11 to get to the worksheet BOF record
            else:
                abs_posn = -1 # unknown
        else:
            offset, visibility, sheet_type = unpack('<iBB', data[0:6])
            abs_posn = offset + self.base # because global BOF is always at posn 0 in the stream
            if bv < BIFF_FIRST_UNICODE:
                sheet_name = unpack_string(data, 6, self.encoding, lenlen=1)
            else:
                sheet_name = unpack_unicode(data, 6, lenlen=1)

        if DEBUG or self.verbosity >= 2:
            fprintf(self.logfile,
                "BOUNDSHEET: inx=%d vis=%r sheet_name=%r abs_posn=%d sheet_type=0x%02x\n",
                self._all_sheets_count, visibility, sheet_name, abs_posn, sheet_type)
        self._all_sheets_count += 1
        if sheet_type != XL_BOUNDSHEET_WORKSHEET:
            self._all_sheets_map.append(-1)
            descr = {
                1: 'Macro sheet',
                2: 'Chart',
                6: 'Visual Basic module',
                }.get(sheet_type, 'UNKNOWN')

            fprintf(self.logfile,
                "NOTE *** Ignoring non-worksheet data named %r (type 0x%02x = %s)\n",
                sheet_name, sheet_type, descr)
        else:
            snum = len(self._sheet_names)
            self._all_sheets_map.append(snum)
            self._sheet_names.append(sheet_name)
            self._sh_abs_posn.append(abs_posn)
            self._sheet_visibility.append(visibility)
            self._sheet_num_from_name[sheet_name] = snum

    def handle_builtinfmtcount(self, data):
        ### N.B. This count appears to be utterly useless.
        # DEBUG = 1
        builtinfmtcount = unpack('<H', data[0:2])[0]
        if DEBUG: fprintf(self.logfile, "BUILTINFMTCOUNT: %r\n", builtinfmtcount)
        self.builtinfmtcount = builtinfmtcount

    def derive_encoding(self):
        if self.encoding_override:
            self.encoding = self.encoding_override
        elif self.codepage is None:
            if self.biff_version < 80:
                fprintf(self.logfile,
                    "*** No CODEPAGE record, no encoding_override: will use 'ascii'\n")
                self.encoding = 'ascii'
            else:
                self.codepage = 1200 # utf16le
                if self.verbosity >= 2:
                    fprintf(self.logfile, "*** No CODEPAGE record; assuming 1200 (utf_16_le)\n")
        else:
            codepage = self.codepage
            if encoding_from_codepage.has_key(codepage):
                encoding = encoding_from_codepage[codepage]
            elif 300 <= codepage <= 1999:
                encoding = 'cp' + str(codepage)
            else:
                encoding = 'unknown_codepage_' + str(codepage)
            if DEBUG or (self.verbosity and encoding != self.encoding) :
                fprintf(self.logfile, "CODEPAGE: codepage %r -> encoding %r\n", codepage, encoding)
            self.encoding = encoding
        if self.codepage != 1200: # utf_16_le
            # If we don't have a codec that can decode ASCII into Unicode,
            # we're well & truly stuffed -- let the punter know ASAP.
            try:
                _unused = unicode('trial', self.encoding)
            except:
                ei = sys.exc_info()[:2]
                fprintf(self.logfile,
                    "ERROR *** codepage %r -> encoding %r -> %s: %s\n",
                    self.codepage, self.encoding, ei[0].__name__.split(".")[-1], ei[1])
                raise
        if self.raw_user_name:
            strg = unpack_string(self.user_name, 0, self.encoding, lenlen=1)
            strg = strg.rstrip()
            # if DEBUG:
            #     print "CODEPAGE: user name decoded from %r to %r" % (self.user_name, strg)
            self.user_name = strg
            self.raw_user_name = False
        return self.encoding

    def handle_codepage(self, data):
        # DEBUG = 0
        codepage = unpack('<H', data[0:2])[0]
        self.codepage = codepage
        self.derive_encoding()

    def handle_country(self, data):
        countries = unpack('<HH', data[0:4])
        if self.verbosity: print >> self.logfile, "Countries:", countries
        # Note: in BIFF7 and earlier, country record was put (redundantly?) in each worksheet.
        assert self.countries == (0, 0) or self.countries == countries
        self.countries = countries

    def handle_datemode(self, data):
        datemode = unpack('<H', data[0:2])[0]
        if DEBUG or self.verbosity:
            fprintf(self.logfile, "DATEMODE: datemode %r\n", datemode)
        assert datemode in (0, 1)
        self.datemode = datemode

    def handle_externname(self, data):
        blah = DEBUG or self.verbosity >= 2
        if self.biff_version >= 80:
            option_flags, other_info =unpack("<HI", data[:6])
            pos = 6
            name, pos = unpack_unicode_update_pos(data, pos, lenlen=1)
            extra = data[pos:]
            if self._supbook_types[-1] == SUPBOOK_ADDIN:
                self.addin_func_names.append(name)
            if blah:
                fprintf(self.logfile,
                    "EXTERNNAME: sbktype=%d oflags=0x%04x oinfo=0x%08x name=%r extra=%r\n",
                    self._supbook_types[-1], option_flags, other_info, name, extra)

    def handle_externsheet(self, data):
        self.derive_encoding() # in case CODEPAGE record missing/out of order/wrong
        self._extnsht_count += 1 # for use as a 1-based index
        blah1 = DEBUG or self.verbosity >= 1
        blah2 = DEBUG or self.verbosity >= 2
        if self.biff_version >= 80:
            num_refs = unpack("<H", data[0:2])[0]
            bytes_reqd = num_refs * 6 + 2
            while len(data) < bytes_reqd:
                if blah1:
                    fprintf(
                        self.logfile,
                        "INFO: EXTERNSHEET needs %d bytes, have %d\n",
                        bytes_reqd, len(data),
                        )
                code2, length2, data2 = self.get_record_parts()
                if code2 != XL_CONTINUE:
                    raise XLRDError("Missing CONTINUE after EXTERNSHEET record")
                data += data2
            pos = 2
            for k in xrange(num_refs):
                info = unpack("<HHH", data[pos:pos+6])
                ref_recordx, ref_first_sheetx, ref_last_sheetx = info
                self._externsheet_info.append(info)
                pos += 6
                if blah2:
                    fprintf(
                        self.logfile,
                        "EXTERNSHEET(b8): k = %2d, record = %2d, first_sheet = %5d, last sheet = %5d\n",
                        k, ref_recordx, ref_first_sheetx, ref_last_sheetx,
                        )
        else:
            nc, ty = unpack("<BB", data[:2])
            if blah2:
                print "EXTERNSHEET(b7-):"
                hex_char_dump(data, 0, len(data))
                msg = {
                    1: "Encoded URL",
                    2: "Current sheet!!",
                    3: "Specific sheet in own doc't",
                    4: "Nonspecific sheet in own doc't!!",
                    }.get(ty, "Not encoded")
                print "   %3d chars, type is %d (%s)" % (nc, ty, msg)
            if ty == 3:
                sheet_name = unicode(data[2:nc+2], self.encoding)
                self._extnsht_name_from_num[self._extnsht_count] = sheet_name
                if blah2: print self._extnsht_name_from_num
            if not (1 <= ty <= 4):
                ty = 0
            self._externsheet_type_b57.append(ty)

    def handle_filepass(self, data):
        if self.verbosity >= 2:
            logf = self.logfile
            fprintf(logf, "FILEPASS:\n")
            hex_char_dump(data, 0, len(data), base=0, fout=logf)
            if self.biff_version >= 80:
                kind1, = unpack('<H', data[:2])
                if kind1 == 0: # weak XOR encryption
                    key, hash_value = unpack('<HH', data[2:])
                    fprintf(logf,
                        'weak XOR: key=0x%04x hash=0x%04x\n',
                        key, hash_value)
                elif kind1 == 1:
                    kind2, = unpack('<H', data[4:6])
                    if kind2 == 1: # BIFF8 standard encryption
                        caption = "BIFF8 std"
                    elif kind2 == 2:
                        caption = "BIFF8 strong"
                    else:
                        caption = "** UNKNOWN ENCRYPTION METHOD **"
                    fprintf(logf, "%s\n", caption)
        raise XLRDError("Workbook is encrypted")

    def handle_name(self, data):
        blah = DEBUG or self.verbosity >= 2
        bv = self.biff_version
        if bv < 50:
            return
        self.derive_encoding()
        # print
        # hex_char_dump(data, 0, len(data))
        (
        option_flags, kb_shortcut, name_len, fmla_len, extsht_index, sheet_index,
        menu_text_len, description_text_len, help_topic_text_len, status_bar_text_len,
        ) = unpack("<HBBHHH4B", data[0:14])
        nobj = Name()
        nobj.book = self ### CIRCULAR ###
        name_index = len(self.name_obj_list)
        nobj.name_index = name_index
        self.name_obj_list.append(nobj)
        nobj.option_flags = option_flags
        for attr, mask, nshift in (
            ('hidden', 1, 0),
            ('func', 2, 1),
            ('vbasic', 4, 2),
            ('macro', 8, 3),
            ('complex', 0x10, 4),
            ('builtin', 0x20, 5),
            ('funcgroup', 0xFC0, 6),
            ('binary', 0x1000, 12),
            ):
            setattr(nobj, attr, (option_flags & mask) >> nshift)

        macro_flag = " M"[nobj.macro]
        if bv < 80:
            internal_name, pos = unpack_string_update_pos(data, 14, self.encoding, known_len=name_len)
        else:
            internal_name, pos = unpack_unicode_update_pos(data, 14, known_len=name_len)
        nobj.extn_sheet_num = extsht_index
        nobj.excel_sheet_index = sheet_index
        nobj.scope = None # patched up in the names_epilogue() method
        if blah:
            print "NAME[%d]:%s oflags=%d, name_len=%d, fmla_len=%d, extsht_index=%d, sheet_index=%d, name=%r" \
                % (name_index, macro_flag, option_flags, name_len,
                fmla_len, extsht_index, sheet_index, internal_name)
        name = internal_name
        if nobj.builtin:
            name = builtin_name_from_code.get(name, "??Unknown??")
            if blah: print "    builtin: %s" % name
        nobj.name = name
        nobj.raw_formula = data[pos:]
        nobj.basic_formula_len = fmla_len
        nobj.evaluated = 0
        if blah:
            nobj.dump(
                self.logfile,
                header="--- handle_name: name[%d] ---" % name_index,
                footer="-------------------",
                )

    def names_epilogue(self):
        blah = self.verbosity >= 2
        f = self.logfile
        if blah:
            print >> f, "+++++ names_epilogue +++++"
            print >> f, "_all_sheets_map", self._all_sheets_map
            print >> f, "_extnsht_name_from_num", self._extnsht_name_from_num
            print >> f, "_sheet_num_from_name", self._sheet_num_from_name
        num_names = len(self.name_obj_list)
        for namex in range(num_names):
            nobj = self.name_obj_list[namex]
            # Convert from excel_sheet_index to scope.
            # This is done here because in BIFF7 and earlier, the
            # BOUNDSHEET records (from which _all_sheets_map is derived)
            # come after the NAME records.
            if self.biff_version >= 80:
                sheet_index = nobj.excel_sheet_index
                if sheet_index == 0:
                    intl_sheet_index = -1 # global
                elif 1 <= sheet_index <= len(self._all_sheets_map):
                    intl_sheet_index = self._all_sheets_map[sheet_index-1]
                    if intl_sheet_index == -1: # maps to a macro or VBA sheet
                        intl_sheet_index = -2 # valid sheet reference but not useful
                else:
                    # huh?
                    intl_sheet_index = -3 # invalid
            elif 50 <= self.biff_version <= 70:
                sheet_index = nobj.extn_sheet_num
                if sheet_index == 0:
                    intl_sheet_index = -1 # global
                else:
                    sheet_name = self._extnsht_name_from_num[sheet_index]
                    intl_sheet_index = self._sheet_num_from_name.get(sheet_name, -2)
            nobj.scope = intl_sheet_index

        for namex in range(num_names):
            nobj = self.name_obj_list[namex]
            # Parse the formula ...
            if nobj.macro or nobj.binary: continue
            if nobj.evaluated: continue
            evaluate_name_formula(self, nobj, namex, blah=blah)

        if self.verbosity >= 2:
            print >> f, "---------- name object dump ----------"
            for namex in range(num_names):
                nobj = self.name_obj_list[namex]
                nobj.dump(f, header="--- name[%d] ---" % namex)
            print >> f, "--------------------------------------"
        #
        # Build some dicts for access to the name objects
        #
        name_and_scope_map = {} # (name.lower(), scope): Name_object
        name_map = {}           # name.lower() : list of Name_objects (sorted in scope order)
        for namex in range(num_names):
            nobj = self.name_obj_list[namex]
            name_lcase = nobj.name.lower()
            key = (name_lcase, nobj.scope)
            if name_and_scope_map.has_key(key):
                msg = 'Duplicate entry %r in name_and_scope_map' % (key, )
                if 0:
                    raise XLRDError(msg)
                else:
                    if self.verbosity:
                        print >> f, msg
            name_and_scope_map[key] = nobj
            if name_map.has_key(name_lcase):
                name_map[name_lcase].append((nobj.scope, nobj))
            else:
                name_map[name_lcase] = [(nobj.scope, nobj)]
        for key in name_map.keys():
            alist = name_map[key]
            alist.sort()
            name_map[key] = [x[1] for x in alist]
        self.name_and_scope_map = name_and_scope_map
        self.name_map = name_map

    def handle_obj(self, data):
        # Not doing much handling at all.
        # Worrying about embedded (BOF ... EOF) substreams is done elsewhere.
        # DEBUG = 1
        obj_type, obj_id = unpack('<HI', data[4:10])
        # if DEBUG: print "---> handle_obj type=%d id=0x%08x" % (obj_type, obj_id)

    def handle_supbook(self, data):
        self._supbook_types.append(None)
        blah = DEBUG or self.verbosity >= 2
        if 0:
            print "SUPBOOK:"
            hex_char_dump(data, 0, len(data))
        num_sheets = unpack("<H", data[0:2])[0]
        sbn = self._supbook_count
        self._supbook_count += 1
        if data[2:4] == "\x01\x04":
            self._supbook_types[-1] = SUPBOOK_INTERNAL
            self._supbook_locals_inx = self._supbook_count - 1
            if blah:
                print "SUPBOOK[%d]: internal 3D refs; %d sheets" % (sbn, num_sheets)
                print "    _all_sheets_map", self._all_sheets_map
            return
        if data[0:4] == "\x01\x00\x01\x3A":
            self._supbook_types[-1] = SUPBOOK_ADDIN
            self._supbook_addins_inx = self._supbook_count - 1
            if blah: print "SUPBOOK[%d]: add-in functions" % sbn
            return
        url, pos = unpack_unicode_update_pos(data, 2, lenlen=2)
        if num_sheets == 0:
            self._supbook_types[-1] = SUPBOOK_DDEOLE
            if blah: print "SUPBOOK[%d]: DDE/OLE document = %r" % (sbn, url)
            return
        self._supbook_types[-1] = SUPBOOK_EXTERNAL
        if blah: print "SUPBOOK[%d]: url = %r" % (sbn, url)
        sheet_names = []
        for x in range(num_sheets):
            shname, pos = unpack_unicode_update_pos(data, pos, lenlen=2)
            sheet_names.append(shname)
            if blah: print "    sheet %d: %r" % (x, shname)

    def handle_sheethdr(self, data):
        # This a BIFF 4W special.
        # The SHEETHDR record is followed by a (BOF ... EOF) substream containing
        # a worksheet.
        # DEBUG = 1
        self.derive_encoding()
        sheet_len = unpack('<i', data[:4])[0]
        sheet_name = unpack_string(data, 4, self.encoding, lenlen=1)
        sheetno = self._sheethdr_count
        assert sheet_name == self._sheet_names[sheetno]
        self._sheethdr_count += 1
        BOF_posn = self._position
        posn = BOF_posn - 4 - len(data)
        if DEBUG: print >> self.logfile, 'SHEETHDR %d at posn %d: len=%d name=%r' % (sheetno, posn, sheet_len, sheet_name)
        self.initialise_format_info()
        if DEBUG: print >> self.logfile, 'SHEETHDR: xf epilogue flag is %d' % self._xf_epilogue_done
        self._sheet_list.append(None) # get_sheet updates _sheet_list but needs a None beforehand
        self.get_sheet(sheetno, update_pos=False)
        if DEBUG: print >> self.logfile, 'SHEETHDR: posn after get_sheet() =', self._position
        self._position = BOF_posn + sheet_len

    def handle_sheetsoffset(self, data):
        # DEBUG = 0
        posn = unpack('<i', data)[0]
        if DEBUG: print >> self.logfile, 'SHEETSOFFSET:', posn
        self._sheetsoffset = posn

    def handle_sst(self, data):
        # DEBUG = 1
        if DEBUG:
            print >> self.logfile, "SST Processing"
            t0 = time.time()
        nbt = len(data)
        strlist = [data]
        uniquestrings = unpack('<i', data[4:8])[0]
        if DEBUG  or self.verbosity >= 2:
            fprintf(self.logfile, "SST: unique strings: %d\n", uniquestrings)
        while 1:
            code, nb, data = self.get_record_parts_conditional(XL_CONTINUE)
            if code is None:
                break
            nbt += nb
            if DEBUG >= 2:
                fprintf(self.logfile, "CONTINUE: adding %d bytes to SST -> %d\n", nb, nbt)
            strlist.append(data)
        self._sharedstrings = unpack_SST_table(strlist, uniquestrings)
        if DEBUG:
            t1 = time.time()
            print >> self.logfile, "SST processing took %.2f seconds" % (t1 - t0, )

    def handle_writeaccess(self, data):
        # DEBUG = 0
        if self.biff_version < 80:
            if not self.encoding:
                self.raw_user_name = True
                self.user_name = data
                return
            strg = unpack_string(data, 0, self.encoding, lenlen=1)
        else:
            strg = unpack_unicode(data, 0, lenlen=2)
        if DEBUG: print >> self.logfile, "WRITEACCESS: %d bytes; raw=%d %r" % (len(data), self.raw_user_name, strg)
        strg = strg.rstrip()
        self.user_name = strg

    def parse_globals(self):
        # DEBUG = 0
        # no need to position, just start reading (after the BOF)
        formatting.initialise_book(self)
        while 1:
            rc, length, data = self.get_record_parts()
            if DEBUG: print "parse_globals: record code is 0x%04x" % rc
            if rc == XL_SST:
                self.handle_sst(data)
            elif rc == XL_FONT or rc == XL_FONT_B3B4:
                self.handle_font(data)
            elif rc == XL_FORMAT: # XL_FORMAT2 is BIFF <= 3.0, can't appear in globals
                self.handle_format(data)
            elif rc == XL_XF:
                self.handle_xf(data)
            elif rc ==  XL_BOUNDSHEET:
                self.handle_boundsheet(data)
            elif rc == XL_DATEMODE:
                self.handle_datemode(data)
            elif rc == XL_CODEPAGE:
                self.handle_codepage(data)
            elif rc == XL_COUNTRY:
                self.handle_country(data)
            elif rc == XL_EXTERNNAME:
                self.handle_externname(data)
            elif rc == XL_EXTERNSHEET:
                self.handle_externsheet(data)
            elif rc == XL_FILEPASS:
                self.handle_filepass(data)
            elif rc == XL_WRITEACCESS:
                self.handle_writeaccess(data)
            elif rc == XL_SHEETSOFFSET:
                self.handle_sheetsoffset(data)
            elif rc == XL_SHEETHDR:
                self.handle_sheethdr(data)
            elif rc == XL_SUPBOOK:
                self.handle_supbook(data)
            elif rc == XL_NAME:
                self.handle_name(data)
            elif rc == XL_PALETTE:
                self.handle_palette(data)
            elif rc == XL_STYLE:
                self.handle_style(data)
            elif rc & 0xff == 9:
                print >> self.logfile, "*** Unexpected BOF at posn %d: 0x%04x len=%d data=%r" \
                    % (self._position - length - 4, rc, length, data)
            elif rc ==  XL_EOF:
                self.xf_epilogue()
                self.names_epilogue()
                self.palette_epilogue()
                if not self.encoding:
                    self.derive_encoding()
                if self.biff_version == 45:
                    # DEBUG = 0
                    if DEBUG: print "global EOF: position", self._position
                    # if DEBUG:
                    #     pos = self._position - 4
                    #     print repr(self.mem[pos:pos+40])
                return
            else:
                # if DEBUG:
                #     print "parse_globals: ignoring record code 0x%04x" % rc
                pass

    def read(self, pos, length):
        data = self.mem[pos:pos+length]
        self._position = pos + len(data)
        return data

    def getbof(self, rqd_stream):
        # DEBUG = 1
        # if DEBUG: print >> self.logfile, "getbof(): position", self._position
        if DEBUG: print >> self.logfile, "reqd: 0x%04x" % rqd_stream
        def bof_error(msg):
            raise XLRDError('Unsupported format, or corrupt file: ' + msg)
        savpos = self._position
        opcode = self.get2bytes()
        if opcode == MY_EOF:
            bof_error('Expected BOF record; met end of file')
        if opcode not in bofcodes:
            bof_error('Expected BOF record; found %r' % self.mem[savpos:savpos+8])
        length = self.get2bytes()
        if length == MY_EOF:
            bof_error('Incomplete BOF record[1]; met end of file')
        if length < boflen[opcode] or length > 20:
            bof_error(
                'Invalid length (%d) for BOF record type 0x%04x'
                % (length, opcode))
        data = self.read(self._position, length);
        if DEBUG: print >> self.logfile, "\ngetbof(): data=%r" % data
        if len(data) < length:
            bof_error('Incomplete BOF record[2]; met end of file')
        version1 = opcode >> 8
        version2, streamtype = unpack('<HH', data[0:4])
        if DEBUG:
            print >> self.logfile, "getbof(): op=0x%04x version2=0x%04x streamtype=0x%04x" \
                % (opcode, version2, streamtype)
        bof_offset = self._position - 4 - length
        if DEBUG:
            print >> self.logfile, "getbof(): BOF found at offset %d; savpos=%d" \
                % (bof_offset, savpos)
        version = build = year = 0
        if version1 == 0x08:
            build, year = unpack('<HH', data[4:8])
            if version2 == 0x0600:
                version = 80
            elif version2 == 0x0500:
                if year < 1994 or build in (2412, 3218, 3321):
                    version = 50
                else:
                    version = 70
            else:
                # dodgy one, created by a 3rd-party tool
                version = {
                    0x0000: 21,
                    0x0007: 21,
                    0x0200: 21,
                    0x0300: 30,
                    0x0400: 40,
                    }.get(version2, 0)
        elif version1 in (0x04, 0x02, 0x00):
            version = {0x04: 40, 0x02: 30, 0x00: 21}[version1]

        if version == 40 and streamtype == XL_WORKBOOK_GLOBALS_4W:
            version = 45 # i.e. 4W

        if DEBUG or self.verbosity >= 2:
            print >> self.logfile, \
                "BOF: op=0x%04x vers=0x%04x stream=0x%04x buildid=%d buildyr=%d -> BIFF%d" \
                % (opcode, version2, streamtype, build, year, version)
        got_globals = streamtype == XL_WORKBOOK_GLOBALS or (
            version == 45 and streamtype == XL_WORKBOOK_GLOBALS_4W)
        if (rqd_stream == XL_WORKBOOK_GLOBALS and got_globals) or streamtype == rqd_stream:
            return version
        if version < 50 and streamtype == XL_WORKSHEET:
            return version
        if version >= 50 and streamtype == 0x0100:
            bof_error("Workspace file -- no spreadsheet data")
        bof_error(
            'BOF not workbook/worksheet: op=0x%04x vers=0x%04x strm=0x%04x build=%d year=%d -> BIFF%d' \
            % (opcode, version2, streamtype, build, year, version)
            )

# === helper functions

def expand_cell_address(inrow, incol):
    # Ref : OOo docs, "4.3.4 Cell Addresses in BIFF8"
    outrow = inrow
    if incol & 0x8000:
        if outrow >= 32768:
            outrow -= 65536
        relrow = 1
    else:
        relrow = 0
    outcol = incol & 0xFF
    if incol & 0x4000:
        if outcol >= 128:
            outcol -= 256
        relcol = 1
    else:
        relcol = 0
    return outrow, outcol, relrow, relcol

def colname(colx, _A2Z="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    assert colx >= 0
    name = ''
    while 1:
        quot, rem = divmod(colx, 26)
        name = _A2Z[rem] + name
        if not quot:
            return name
        colx = quot - 1

def display_cell_address(rowx, colx, relrow, relcol):
    if relrow:
        rowpart = "(*%s%d)" % ("+-"[rowx < 0], abs(rowx))
    else:
        rowpart = "$%d" % (rowx+1,)
    if relcol:
        colpart = "(*%s%d)" % ("+-"[colx < 0], abs(colx))
    else:
        colpart = "$" + colname(colx)
    return colpart + rowpart

def unpack_SST_table(datatab, nstrings):
    "Return list of strings"
    datainx = 0
    ndatas = len(datatab)
    data = datatab[0]
    datalen = len(data)
    pos = 8
    strings = []
    strappend = strings.append
    local_unpack = unpack
    local_min = min
    local_ord = ord
    latin_1 = "latin_1"
    for _unused_i in xrange(nstrings):
        nchars = local_unpack('<H', data[pos:pos+2])[0]
        pos += 2
        options = local_ord(data[pos])
        pos += 1
        rtsz = 0
        if options & 0x08: # richtext
            rtsz = 4 * local_unpack('<H', data[pos:pos+2])[0]
            pos += 2
        if options & 0x04: # phonetic
            rtsz += local_unpack('<i', data[pos:pos+4])[0]
            pos += 4
        accstrg = u''
        charsgot = 0
        while 1:
            charsneed = nchars - charsgot
            if options & 0x01:
                # Uncompressed UTF-16
                charsavail = local_min((datalen - pos) >> 1, charsneed)
                rawstrg = data[pos:pos+2*charsavail]
                # if DEBUG: print "SST U16: nchars=%d pos=%d rawstrg=%r" % (nchars, pos, rawstrg)
                try:
                    accstrg += unicode(rawstrg, "utf_16_le")
                except:
                    # print "SST U16: nchars=%d pos=%d rawstrg=%r" % (nchars, pos, rawstrg)
                    # Probable cause: dodgy data e.g. unfinished surrogate pair.
                    # E.g. file unicode2.xls in pyExcelerator's examples has cells containing
                    # unichr(i) for i in range(0x100000)
                    # so this will include 0xD800 etc
                    raise
                pos += 2*charsavail
            else:
                # Note: this is COMPRESSED (not ASCII!) encoding!!!
                charsavail = local_min(datalen - pos, charsneed)
                rawstrg = data[pos:pos+charsavail]
                # if DEBUG: print "SST CMPRSD: nchars=%d pos=%d rawstrg=%r" % (nchars, pos, rawstrg)
                accstrg += unicode(rawstrg, latin_1)
                pos += charsavail
            charsgot += charsavail
            if charsgot == nchars:
                break
            datainx += 1
            data = datatab[datainx]
            datalen = len(data)
            options = local_ord(data[0])
            pos = 1
        pos += rtsz # size of richtext & phonetic stuff to skip
        # also allow for the rich text etc being split ...
        if pos >= datalen:
            # adjust to correct position in next record
            pos = pos - datalen
            datainx += 1
            if datainx < ndatas:
                data = datatab[datainx]
                datalen = len(data)
            else:
                assert _unused_i == nstrings - 1
        strappend(accstrg)
    return strings
