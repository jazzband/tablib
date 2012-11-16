# Support module for the xlrd3 package.
#
# Portions copyright (c) 2005-2008 Stephen John Machin, Lingfo Pty Ltd
# This module is part of the xlrd package, which is released under a
# BSD-style licence.
#
# 2010-12-08 mozman refactoring for python 3
# 2008-02-10 SJM BIFF2 BLANK record
# 2008-02-08 SJM Preparation for Excel 2.0 support
# 2008-02-02 SJM Added suffixes (_B2, _B2_ONLY, etc) on record names for
#                biff_dump & biff_count
# 2007-12-04 SJM Added support for Excel 2.x (BIFF2) files.
# 2007-09-08 SJM Avoid crash when zero-length Unicode string missing options byte.
# 2007-04-22 SJM Remove experimental "trimming" facility.

import sys
from struct import unpack

encoding_from_codepage = {
    1200 : 'utf_16_le',
    10000: 'mac_roman',
    10006: 'mac_greek', # guess
    10007: 'mac_cyrillic', # guess
    10029: 'mac_latin2', # guess
    10079: 'mac_iceland', # guess
    10081: 'mac_turkish', # guess
    32768: 'mac_roman',
    32769: 'cp1252',
    }

# some more guessing, for Indic scripts
# codepage 57000 range:
# 2 Devanagari [0]
# 3 Bengali [1]
# 4 Tamil [5]
# 5 Telegu [6]
# 6 Assamese [1] c.f. Bengali
# 7 Oriya [4]
# 8 Kannada [7]
# 9 Malayalam [8]
# 10 Gujarati [3]
# 11 Gurmukhi [2]

FUN = 0 # unknown
FDT = 1 # date
FNU = 2 # number
FGE = 3 # general
FTX = 4 # text

DATEFORMAT = FDT
NUMBERFORMAT = FNU

XL_CELL_EMPTY = 0
XL_CELL_TEXT = 1
XL_CELL_NUMBER = 2
XL_CELL_DATE = 3
XL_CELL_BOOLEAN = 4
XL_CELL_ERROR = 5
XL_CELL_BLANK = 6 # for use in debugging, gathering stats, etc

biff_text_from_num = {
    0:  "(not BIFF)",
    20: "2.0",
    21: "2.1",
    30: "3",
    40: "4S",
    45: "4W",
    50: "5",
    70: "7",
    80: "8",
    85: "8X",
}

# This dictionary can be used to produce a text version of the internal codes
# that Excel uses for error cells. Here are its contents:
error_text_from_code = {
    0x00: '#NULL!',  # Intersection of two cell ranges is empty
    0x07: '#DIV/0!', # Division by zero
    0x0F: '#VALUE!', # Wrong type of operand
    0x17: '#REF!',   # Illegal or deleted cell reference
    0x1D: '#NAME?',  # Wrong function or range name
    0x24: '#NUM!',   # Value range overflow
    0x2A: '#N/A!',   # Argument or function not available
}

BIFF_FIRST_UNICODE = 80

XL_WORKBOOK_GLOBALS = WBKBLOBAL = 0x5
XL_WORKBOOK_GLOBALS_4W = 0x100
XL_WORKSHEET = WRKSHEET = 0x10

XL_BOUNDSHEET_WORKSHEET = 0x00
XL_BOUNDSHEET_CHART     = 0x02
XL_BOUNDSHEET_VB_MODULE = 0x06

# XL_RK2 = 0x7e
XL_ARRAY  = 0x0221
XL_ARRAY2 = 0x0021
XL_BLANK = 0x0201
XL_BLANK_B2 = 0x01
XL_BOF = 0x809
XL_BOOLERR = 0x205
XL_BOOLERR_B2 = 0x5
XL_BOUNDSHEET = 0x85
XL_BUILTINFMTCOUNT = 0x56
XL_CF = 0x01B1
XL_CODEPAGE = 0x42
XL_COLINFO = 0x7D
XL_COLUMNDEFAULT = 0x20 # BIFF2 only
XL_COLWIDTH = 0x24 # BIFF2 only
XL_CONDFMT = 0x01B0
XL_CONTINUE = 0x3c
XL_COUNTRY = 0x8C
XL_DATEMODE = 0x22
XL_DEFAULTROWHEIGHT = 0x0225
XL_DEFCOLWIDTH = 0x55
XL_DIMENSION = 0x200
XL_DIMENSION2 = 0x0
XL_EFONT = 0x45
XL_EOF = 0x0a
XL_EXTERNNAME = 0x23
XL_EXTERNSHEET = 0x17
XL_EXTSST = 0xff
XL_FEAT11 = 0x872
XL_FILEPASS = 0x2f
XL_FONT = 0x31
XL_FONT_B3B4 = 0x231
XL_FORMAT = 0x41e
XL_FORMAT2 = 0x1E # BIFF2, BIFF3
XL_FORMULA = 0x6
XL_FORMULA3 = 0x206
XL_FORMULA4 = 0x406
XL_GCW = 0xab
XL_INDEX = 0x20b
XL_INTEGER = 0x2 # BIFF2 only
XL_IXFE = 0x44 # BIFF2 only
XL_LABEL = 0x204
XL_LABEL_B2 = 0x04
XL_LABELRANGES = 0x15f
XL_LABELSST = 0xfd
XL_MERGEDCELLS = 0xE5
XL_MSO_DRAWING = 0x00EC
XL_MSO_DRAWING_GROUP = 0x00EB
XL_MSO_DRAWING_SELECTION = 0x00ED
XL_MULRK = 0xbd
XL_MULBLANK = 0xbe
XL_NAME = 0x18
XL_NOTE = 0x1c
XL_NUMBER = 0x203
XL_NUMBER_B2 = 0x3
XL_OBJ = 0x5D
XL_PALETTE = 0x92
XL_RK = 0x27e
XL_ROW = 0x208
XL_ROW_B2 = 0x08
XL_RSTRING = 0xd6
XL_SHEETHDR = 0x8F # BIFF4W only
XL_SHEETSOFFSET = 0x8E # BIFF4W only
XL_SHRFMLA = 0x04bc
XL_SST = 0xfc
XL_STANDARDWIDTH = 0x99
XL_STRING = 0x207
XL_STRING_B2 = 0x7
XL_STYLE = 0x293
XL_SUPBOOK = 0x1AE
XL_TABLEOP = 0x236
XL_TABLEOP2 = 0x37
XL_TABLEOP_B2 = 0x36
XL_TXO = 0x1b6
XL_UNCALCED = 0x5e
XL_UNKNOWN = 0xffff
XL_WINDOW2 = 0x023E
XL_WRITEACCESS = 0x5C
XL_XF = 0xe0
XL_XF2 = 0x0043 # BIFF2 version of XF record
XL_XF3 = 0x0243 # BIFF3 version of XF record
XL_XF4 = 0x0443 # BIFF4 version of XF record

boflen = {
    0x0809: 8,
    0x0409: 6,
    0x0209: 6,
    0x0009: 4,
}

bofcodes = (0x0809, 0x0409, 0x0209, 0x0009)

XL_FORMULA_OPCODES = (0x0006, 0x0406, 0x0206)

_cell_opcode_list = (
    XL_BOOLERR,
    XL_FORMULA,
    XL_FORMULA3,
    XL_FORMULA4,
    XL_LABEL,
    XL_LABELSST,
    XL_MULRK,
    XL_NUMBER,
    XL_RK,
    XL_RSTRING,
)

biff_rec_name_dict = {
    0x0000: 'DIMENSIONS_B2',
    0x0001: 'BLANK_B2',
    0x0002: 'INTEGER_B2_ONLY',
    0x0003: 'NUMBER_B2',
    0x0004: 'LABEL_B2',
    0x0005: 'BOOLERR_B2',
    0x0006: 'FORMULA',
    0x0007: 'STRING_B2',
    0x0008: 'ROW_B2',
    0x0009: 'BOF_B2',
    0x000A: 'EOF',
    0x000B: 'INDEX_B2_ONLY',
    0x000C: 'CALCCOUNT',
    0x000D: 'CALCMODE',
    0x000E: 'PRECISION',
    0x000F: 'REFMODE',
    0x0010: 'DELTA',
    0x0011: 'ITERATION',
    0x0012: 'PROTECT',
    0x0013: 'PASSWORD',
    0x0014: 'HEADER',
    0x0015: 'FOOTER',
    0x0016: 'EXTERNCOUNT',
    0x0017: 'EXTERNSHEET',
    0x0018: 'NAME_B2,5+',
    0x0019: 'WINDOWPROTECT',
    0x001A: 'VERTICALPAGEBREAKS',
    0x001B: 'HORIZONTALPAGEBREAKS',
    0x001C: 'NOTE',
    0x001D: 'SELECTION',
    0x001E: 'FORMAT_B2-3',
    0x001F: 'BUILTINFMTCOUNT_B2',
    0x0020: 'COLUMNDEFAULT_B2_ONLY',
    0x0021: 'ARRAY_B2_ONLY',
    0x0022: 'DATEMODE',
    0x0023: 'EXTERNNAME',
    0x0024: 'COLWIDTH_B2_ONLY',
    0x0025: 'DEFAULTROWHEIGHT_B2_ONLY',
    0x0026: 'LEFTMARGIN',
    0x0027: 'RIGHTMARGIN',
    0x0028: 'TOPMARGIN',
    0x0029: 'BOTTOMMARGIN',
    0x002A: 'PRINTHEADERS',
    0x002B: 'PRINTGRIDLINES',
    0x002F: 'FILEPASS',
    0x0031: 'FONT',
    0x0032: 'FONT2_B2_ONLY',
    0x0036: 'TABLEOP_B2',
    0x0037: 'TABLEOP2_B2',
    0x003C: 'CONTINUE',
    0x003D: 'WINDOW1',
    0x003E: 'WINDOW2_B2',
    0x0040: 'BACKUP',
    0x0041: 'PANE',
    0x0042: 'CODEPAGE',
    0x0043: 'XF_B2',
    0x0044: 'IXFE_B2_ONLY',
    0x0045: 'EFONT_B2_ONLY',
    0x004D: 'PLS',
    0x0051: 'DCONREF',
    0x0055: 'DEFCOLWIDTH',
    0x0056: 'BUILTINFMTCOUNT_B3-4',
    0x0059: 'XCT',
    0x005A: 'CRN',
    0x005B: 'FILESHARING',
    0x005C: 'WRITEACCESS',
    0x005D: 'OBJECT',
    0x005E: 'UNCALCED',
    0x005F: 'SAVERECALC',
    0x0063: 'OBJECTPROTECT',
    0x007D: 'COLINFO',
    0x007E: 'RK2_mythical_?',
    0x0080: 'GUTS',
    0x0081: 'WSBOOL',
    0x0082: 'GRIDSET',
    0x0083: 'HCENTER',
    0x0084: 'VCENTER',
    0x0085: 'BOUNDSHEET',
    0x0086: 'WRITEPROT',
    0x008C: 'COUNTRY',
    0x008D: 'HIDEOBJ',
    0x008E: 'SHEETSOFFSET',
    0x008F: 'SHEETHDR',
    0x0090: 'SORT',
    0x0092: 'PALETTE',
    0x0099: 'STANDARDWIDTH',
    0x009B: 'FILTERMODE',
    0x009C: 'FNGROUPCOUNT',
    0x009D: 'AUTOFILTERINFO',
    0x009E: 'AUTOFILTER',
    0x00A0: 'SCL',
    0x00A1: 'SETUP',
    0x00AB: 'GCW',
    0x00BD: 'MULRK',
    0x00BE: 'MULBLANK',
    0x00C1: 'MMS',
    0x00D6: 'RSTRING',
    0x00D7: 'DBCELL',
    0x00DA: 'BOOKBOOL',
    0x00DD: 'SCENPROTECT',
    0x00E0: 'XF',
    0x00E1: 'INTERFACEHDR',
    0x00E2: 'INTERFACEEND',
    0x00E5: 'MERGEDCELLS',
    0x00E9: 'BITMAP',
    0x00EB: 'MSO_DRAWING_GROUP',
    0x00EC: 'MSO_DRAWING',
    0x00ED: 'MSO_DRAWING_SELECTION',
    0x00EF: 'PHONETIC',
    0x00FC: 'SST',
    0x00FD: 'LABELSST',
    0x00FF: 'EXTSST',
    0x013D: 'TABID',
    0x015F: 'LABELRANGES',
    0x0160: 'USESELFS',
    0x0161: 'DSF',
    0x01AE: 'SUPBOOK',
    0x01AF: 'PROTECTIONREV4',
    0x01B0: 'CONDFMT',
    0x01B1: 'CF',
    0x01B2: 'DVAL',
    0x01B6: 'TXO',
    0x01B7: 'REFRESHALL',
    0x01B8: 'HLINK',
    0x01BC: 'PASSWORDREV4',
    0x01BE: 'DV',
    0x01C0: 'XL9FILE',
    0x01C1: 'RECALCID',
    0x0200: 'DIMENSIONS',
    0x0201: 'BLANK',
    0x0203: 'NUMBER',
    0x0204: 'LABEL',
    0x0205: 'BOOLERR',
    0x0206: 'FORMULA_B3',
    0x0207: 'STRING',
    0x0208: 'ROW',
    0x0209: 'BOF',
    0x020B: 'INDEX_B3+',
    0x0218: 'NAME',
    0x0221: 'ARRAY',
    0x0223: 'EXTERNNAME_B3-4',
    0x0225: 'DEFAULTROWHEIGHT',
    0x0231: 'FONT_B3B4',
    0x0236: 'TABLEOP',
    0x023E: 'WINDOW2',
    0x0243: 'XF_B3',
    0x027E: 'RK',
    0x0293: 'STYLE',
    0x0406: 'FORMULA_B4',
    0x0409: 'BOF',
    0x041E: 'FORMAT',
    0x0443: 'XF_B4',
    0x04BC: 'SHRFMLA',
    0x0800: 'QUICKTIP',
    0x0809: 'BOF',
    0x0862: 'SHEETLAYOUT',
    0x0867: 'SHEETPROTECTION',
    0x0868: 'RANGEPROTECTION',
}

class XLRDError(Exception):
    pass

class BaseObject:
    """
    Parent of almost all other classes in the package. Defines a common
    'dump' method for debugging.
    """
    _repr_these = []

    def dump(self, f=None, header=None, footer=None, indent=0):
        """
        :param f: open file object, to which the dump is written
        :param header: text to write before the dump
        :param footer: text to write after the dump
        :param indent: number of leading spaces (for recursive calls)
        """
        if f is None:
            f = sys.stderr
        pad = " " * indent

        if header is not None:
            print(header, file=f)

        for attr, value in sorted(self.__dict__.items()):
            if getattr(value, 'dump', None) and attr != 'book':
                value.dump(f,
                    header="%s%s (%s object):" % (pad, attr, value.__class__.__name__),
                    indent=indent+4)
            elif attr not in self._repr_these and \
                 (isinstance(value, list) or
                  isinstance(value, dict)):
                print("%s%s: %s, len = %d" % (pad, attr, type(value), len(value)), file=f)
            else:
                print("%s%s: %r" % (pad, attr, value), file=f)
        if footer is not None:
            print(footer, file=f)

def fprintf(f, fmt, *vargs):
    print(fmt.rstrip('\n') % vargs, file=f)

def upkbits(tgt_obj, src, manifest, local_setattr=setattr):
    for n, mask, attr in manifest:
        local_setattr(tgt_obj, attr, (src & mask) >> n)

def upkbitsL(tgt_obj, src, manifest, local_setattr=setattr, local_int=int):
    for n, mask, attr in manifest:
        local_setattr(tgt_obj, attr, local_int((src & mask) >> n))

def unpack_string(data, pos, encoding, lenlen=1):
    nchars = unpack('<' + 'BH'[lenlen-1], data[pos:pos+lenlen])[0]
    pos += lenlen
    return str(data[pos:pos+nchars], encoding)

def unpack_string_update_pos(data, pos, encoding, lenlen=1, known_len=None):
    if known_len is not None:
        # On a NAME record, the length byte is detached from the front of the string.
        nchars = known_len
    else:
        nchars = unpack('<' + 'BH'[lenlen-1], data[pos:pos+lenlen])[0]
        pos += lenlen

    newpos = pos + nchars
    return (str(data[pos:newpos], encoding), newpos)

def unpack_unicode(data, pos, lenlen=2):
    """ Return unicode_strg """
    nchars = unpack('<' + 'BH'[lenlen-1], data[pos:pos+lenlen])[0]
    if not nchars:
        # Ambiguous whether 0-length string should have an "options" byte.
        # Avoid crash if missing.
        return ""
    pos += lenlen
    options = data[pos]
    pos += 1

    if options & 0x08: # richtext
        pos += 2

    if options & 0x04: # phonetic
        pos += 4

    if options & 0x01:
        # Uncompressed UTF-16-LE
        rawstrg = data[pos:pos+2*nchars]
        strg = str(rawstrg, 'utf_16_le')
    else:
        # Note: this is COMPRESSED (not ASCII!) encoding!!!
        # Merely returning the raw bytes would work OK 99.99% of the time
        # if the local codepage was cp1252 -- however this would rapidly go pear-shaped
        # for other codepages so we grit our Anglocentric teeth and return Unicode :-)
        strg = str(data[pos:pos+nchars], "latin_1")
    return strg

def unpack_unicode_update_pos(data, pos, lenlen=2, known_len=None):
    """ Return (unicode_strg, updated value of pos) """
    if known_len is not None:
        # On a NAME record, the length byte is detached from the front of the string.
        nchars = known_len
    else:
        nchars = unpack('<' + 'BH'[lenlen-1], data[pos:pos+lenlen])[0]
        pos += lenlen

    if not nchars and not data[pos:]:
        # Zero-length string with no options byte
        return ("", pos)

    options = data[pos]
    pos += 1
    phonetic = options & 0x04
    richtext = options & 0x08

    if richtext:
        rt = unpack('<H', data[pos:pos+2])[0]
        pos += 2

    if phonetic:
        sz = unpack('<i', data[pos:pos+4])[0]
        pos += 4

    if options & 0x01:
        # Uncompressed UTF-16-LE
        strg = str(data[pos:pos+2*nchars], 'utf_16_le')
        pos += 2*nchars
    else:
        # Note: this is COMPRESSED (not ASCII!) encoding!!!
        strg = str(data[pos:pos+nchars], "latin_1")
        pos += nchars

    if richtext:
        pos += 4 * rt

    if phonetic:
        pos += sz

    return (strg, pos)

def unpack_cell_range_address_list_update_pos(
    output_list, data, pos, biff_version, addr_size=6):
    # output_list is updated in situ
    if biff_version < 80:
        assert addr_size == 6
    else:
        assert addr_size in (6, 8)
    n, = unpack("<H", data[pos:pos+2])
    pos += 2
    if n:
        fmt = "<HHBB" if addr_size == 6 else "<HHHH"
        for _unused in range(n):
            ra, rb, ca, cb = unpack(fmt, data[pos:pos+addr_size])
            output_list.append((ra, rb+1, ca, cb+1))
            pos += addr_size
    return pos

def hex_char_dump(strg, ofs, dlen, base=0, fout=sys.stdout, unnumbered=False):
    endpos = min(ofs + dlen, len(strg))
    pos = ofs
    numbered = not unnumbered
    num_prefix = ''
    while pos < endpos:
        endsub = min(pos + 16, endpos)
        substrg = strg[pos:endsub]
        lensub = endsub - pos
        if lensub <= 0 or lensub != len(substrg):
            fprintf(
                sys.stdout,
                '??? hex_char_dump: ofs=%d dlen=%d base=%d -> endpos=%d pos=%d endsub=%d substrg=%r\n',
                ofs, dlen, base, endpos, pos, endsub, substrg)
            break
        hexd = ''.join(["%02x " % c for c in substrg])
        chard = ''
        for c in substrg:
            if c == ord('\0'):
                c = '~'
            elif not (' ' <= chr(c) <= '~'):
                c = '?'
            if isinstance(c, int):
                c = chr(c)
            chard += c
        if numbered:
            num_prefix = "%5d: " %  (base+pos-ofs)
        fprintf(fout, "%s     %-48s %s\n", num_prefix, hexd, chard)
        pos = endsub

def biff_dump(mem, stream_offset, stream_len, base=0, fout=sys.stdout,
              unnumbered=False):
    pos = stream_offset
    stream_end = stream_offset + stream_len
    adj = base - stream_offset
    dummies = 0
    numbered = not unnumbered
    num_prefix = ''
    while stream_end - pos >= 4:
        rc, length = unpack('<HH', mem[pos:pos+4])
        if rc == 0 and length == 0:
            if mem[pos:] == '\0' * (stream_end - pos):
                dummies = stream_end - pos
                savpos = pos
                pos = stream_end
                break

            if dummies:
                dummies += 4
            else:
                savpos = pos
                dummies = 4
            pos += 4
        else:
            if dummies:
                if numbered:
                    num_prefix =  "%5d: " % (adj + savpos)
                fprintf(fout, "%s---- %d zero bytes skipped ----\n",
                        num_prefix, dummies)
                dummies = 0

            recname = biff_rec_name_dict.get(rc, '<UNKNOWN>')
            if numbered:
                num_prefix = "%5d: " % (adj + pos)
            fprintf(fout, "%s%04x %s len = %04x (%d)\n",
                    num_prefix, rc, recname, length, length)
            pos += 4
            hex_char_dump(mem, pos, length, adj+pos, fout, unnumbered)
            pos += length
    if dummies:
        if numbered:
            num_prefix =  "%5d: " % (adj + savpos)
        fprintf(fout, "%s---- %d zero bytes skipped ----\n", num_prefix, dummies)

    if pos < stream_end:
        if numbered:
            num_prefix = "%5d: " % (adj + pos)
        fprintf(fout, "%s---- Misc bytes at end ----\n", num_prefix)
        hex_char_dump(mem, pos, stream_end-pos, adj + pos, fout, unnumbered)
    elif pos > stream_end:
        fprintf(fout, "Last dumped record has length (%d) that is too large\n", length)

def biff_count_records(mem, stream_offset, stream_len, fout=sys.stdout):
    pos = stream_offset
    stream_end = stream_offset + stream_len
    tally = {}
    while stream_end - pos >= 4:
        rc, length = unpack('<HH', mem[pos:pos+4])
        if rc == 0 and length == 0:
            if mem[pos:] == '\0' * (stream_end - pos):
                break
            recname = "<Dummy (zero)>"
        else:
            recname = biff_rec_name_dict.get(rc, None)
            if recname is None:
                recname = "Unknown_0x%04X" % rc
        if recname in tally:
            tally[recname] += 1
        else:
            tally[recname] = 1
        pos += length + 4
    for recname, count in sorted(tally.items()):
        fprintf(fout, "%8d %s", count, recname)
