# -*- coding: windows-1252 -*-

import Formatting
from BIFFRecords import *

FIRST_USER_DEFINED_NUM_FORMAT_IDX = 164

class XFStyle(object):

    def __init__(self):
        self.num_format_str  = 'General'
        self.font            = Formatting.Font()
        self.alignment       = Formatting.Alignment()
        self.borders         = Formatting.Borders()
        self.pattern         = Formatting.Pattern()
        self.protection      = Formatting.Protection()

default_style = XFStyle()

class StyleCollection(object):
    _std_num_fmt_list = [
            'general',
            '0',
            '0.00',
            '#,##0',
            '#,##0.00',
            '"$"#,##0_);("$"#,##',
            '"$"#,##0_);[Red]("$"#,##',
            '"$"#,##0.00_);("$"#,##',
            '"$"#,##0.00_);[Red]("$"#,##',
            '0%',
            '0.00%',
            '0.00E+00',
            '# ?/?',
            '# ??/??',
            'M/D/YY',
            'D-MMM-YY',
            'D-MMM',
            'MMM-YY',
            'h:mm AM/PM',
            'h:mm:ss AM/PM',
            'h:mm',
            'h:mm:ss',
            'M/D/YY h:mm',
            '_(#,##0_);(#,##0)',
            '_(#,##0_);[Red](#,##0)',
            '_(#,##0.00_);(#,##0.00)',
            '_(#,##0.00_);[Red](#,##0.00)',
            '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"_);_(@_)',
            '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)',
            '_("$"* #,##0.00_);_("$"* (#,##0.00);_("$"* "-"??_);_(@_)',
            '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)',
            'mm:ss',
            '[h]:mm:ss',
            'mm:ss.0',
            '##0.0E+0',
            '@'
    ]

    def __init__(self, style_compression=0):
        self.style_compression = style_compression
        self.stats = [0, 0, 0, 0, 0, 0]
        self._font_id2x = {}
        self._font_x2id = {}
        self._font_val2x = {}

        for x in (0, 1, 2, 3, 5): # The font with index 4 is omitted in all BIFF versions
            font = Formatting.Font()
            search_key = font._search_key()
            self._font_id2x[font] = x
            self._font_x2id[x] = font
            self._font_val2x[search_key] = x

        self._xf_id2x = {}
        self._xf_x2id = {}
        self._xf_val2x = {}

        self._num_formats = {}
        for fmtidx, fmtstr in zip(range(0, 23), StyleCollection._std_num_fmt_list[0:23]):
            self._num_formats[fmtstr] = fmtidx
        for fmtidx, fmtstr in zip(range(37, 50), StyleCollection._std_num_fmt_list[23:]):
            self._num_formats[fmtstr] = fmtidx

        self.default_style = XFStyle()
        self._default_xf = self._add_style(self.default_style)[0]

    def add(self, style):
        if style == None:
            return 0x10
        return self._add_style(style)[1]

    def _add_style(self, style):
        num_format_str = style.num_format_str
        if num_format_str in self._num_formats:
            num_format_idx = self._num_formats[num_format_str]
        else:
            num_format_idx = (
                FIRST_USER_DEFINED_NUM_FORMAT_IDX
                + len(self._num_formats)
                - len(StyleCollection._std_num_fmt_list)
                )
            self._num_formats[num_format_str] = num_format_idx

        font = style.font
        if font in self._font_id2x:
            font_idx = self._font_id2x[font]
            self.stats[0] += 1
        elif self.style_compression:
            search_key = font._search_key()
            font_idx = self._font_val2x.get(search_key)
            if font_idx is not None:
                self._font_id2x[font] = font_idx
                self.stats[1] += 1
            else:
                font_idx = len(self._font_x2id) + 1 # Why plus 1? Font 4 is missing
                self._font_id2x[font] = font_idx
                self._font_val2x[search_key] = font_idx
                self._font_x2id[font_idx] = font
                self.stats[2] += 1
        else:
            font_idx = len(self._font_id2x) + 1
            self._font_id2x[font] = font_idx
            self.stats[2] += 1

        gof = (style.alignment, style.borders, style.pattern, style.protection)
        xf = (font_idx, num_format_idx) + gof
        if xf in self._xf_id2x:
            xf_index = self._xf_id2x[xf]
            self.stats[3] += 1
        elif self.style_compression == 2:
            xf_key = (font_idx, num_format_idx) + tuple([obj._search_key() for obj in gof])
            xf_index = self._xf_val2x.get(xf_key)
            if xf_index is not None:
                self._xf_id2x[xf] = xf_index
                self.stats[4] += 1
            else:
                xf_index = 0x10 + len(self._xf_x2id)
                self._xf_id2x[xf] = xf_index
                self._xf_val2x[xf_key] = xf_index
                self._xf_x2id[xf_index] = xf
                self.stats[5] += 1
        else:
            xf_index = 0x10 + len(self._xf_id2x)
            self._xf_id2x[xf] = xf_index
            self.stats[5] += 1

        if xf_index >= 0xFFF:
            # 12 bits allowed, 0xFFF is a sentinel value
            raise ValueError("More than 4094 XFs (styles)")

        return xf, xf_index

    def get_biff_data(self):
        result = ''
        result += self._all_fonts()
        result += self._all_num_formats()
        result += self._all_cell_styles()
        result += self._all_styles()
        return result

    def _all_fonts(self):
        result = ''
        if self.style_compression:
            alist = self._font_x2id.items()
        else:
            alist = [(x, o) for o, x in self._font_id2x.items()]
        alist.sort()
        for font_idx, font in alist:
            result += font.get_biff_record().get()
        return result

    def _all_num_formats(self):
        result = ''
        alist = [
            (v, k)
            for k, v in self._num_formats.items()
            if v >= FIRST_USER_DEFINED_NUM_FORMAT_IDX
            ]
        alist.sort()
        for fmtidx, fmtstr in alist:
            result += NumberFormatRecord(fmtidx, fmtstr).get()
        return result

    def _all_cell_styles(self):
        result = ''
        for i in range(0, 16):
            result += XFRecord(self._default_xf, 'style').get()
        if self.style_compression == 2:
            alist = self._xf_x2id.items()
        else:
            alist = [(x, o) for o, x in self._xf_id2x.items()]
        alist.sort()
        for xf_idx, xf in alist:
            result += XFRecord(xf).get()
        return result

    def _all_styles(self):
        return StyleRecord().get()

# easyxf and its supporting objects ###################################

class EasyXFException(Exception):
    pass

class EasyXFCallerError(EasyXFException):
    pass

class EasyXFAuthorError(EasyXFException):
    pass

class IntULim(object):
    # If astring represents a valid unsigned integer ('123', '0xabcd', etc)
    # and it is <= limit, return the int value; otherwise return None.

    def __init__(self, limit):
        self.limit = limit

    def __call__(self, astring):
        try:
            value = int(astring, 0)
        except ValueError:
            return None
        if not 0 <= value <= self.limit:
            return None
        return value

bool_map = {
    # Text values for all Boolean attributes
    '1': 1, 'yes': 1, 'true':  1, 'on':  1,
    '0': 0, 'no':  0, 'false': 0, 'off': 0,
    }

border_line_map = {
    # Text values for these borders attributes:
    # left, right, top, bottom and diag
    'no_line':  0x00,
    'thin':     0x01,
    'medium':   0x02,
    'dashed':   0x03,
    'dotted':   0x04,
    'thick':    0x05,
    'double':   0x06,
    'hair':     0x07,
    'medium_dashed':                0x08,
    'thin_dash_dotted':             0x09,
    'medium_dash_dotted':           0x0a,
    'thin_dash_dot_dotted':         0x0b,
    'medium_dash_dot_dotted':       0x0c,
    'slanted_medium_dash_dotted':   0x0d,
    }

charset_map = {
    # Text values for font.charset
    'ansi_latin':           0x00,
    'sys_default':          0x01,
    'symbol':               0x02,
    'apple_roman':          0x4d,
    'ansi_jap_shift_jis':   0x80,
    'ansi_kor_hangul':      0x81,
    'ansi_kor_johab':       0x82,
    'ansi_chinese_gbk':     0x86,
    'ansi_chinese_big5':    0x88,
    'ansi_greek':           0xa1,
    'ansi_turkish':         0xa2,
    'ansi_vietnamese':      0xa3,
    'ansi_hebrew':          0xb1,
    'ansi_arabic':          0xb2,
    'ansi_baltic':          0xba,
    'ansi_cyrillic':        0xcc,
    'ansi_thai':            0xde,
    'ansi_latin_ii':        0xee,
    'oem_latin_i':          0xff,
    }


# Text values for colour indices. "grey" is a synonym of "gray".
# The names are those given by Microsoft Excel 2003 to the colours
# in the default palette. There is no great correspondence with
# any W3C name-to-RGB mapping.
_colour_map_text = """\
aqua 0x31
black 0x08
blue 0x0C
blue_gray 0x36
bright_green 0x0B
brown 0x3C
coral 0x1D
cyan_ega 0x0F
dark_blue 0x12
dark_blue_ega 0x12
dark_green 0x3A
dark_green_ega 0x11
dark_purple 0x1C
dark_red 0x10
dark_red_ega 0x10
dark_teal 0x38
dark_yellow 0x13
gold 0x33
gray_ega 0x17
gray25 0x16
gray40 0x37
gray50 0x17
gray80 0x3F
green 0x11
ice_blue 0x1F
indigo 0x3E
ivory 0x1A
lavender 0x2E
light_blue 0x30
light_green 0x2A
light_orange 0x34
light_turquoise 0x29
light_yellow 0x2B
lime 0x32
magenta_ega 0x0E
ocean_blue 0x1E
olive_ega 0x13
olive_green 0x3B
orange 0x35
pale_blue 0x2C
periwinkle 0x18
pink 0x0E
plum 0x3D
purple_ega 0x14
red 0x0A
rose 0x2D
sea_green 0x39
silver_ega 0x16
sky_blue 0x28
tan 0x2F
teal 0x15
teal_ega 0x15
turquoise 0x0F
violet 0x14
white 0x09
yellow 0x0D"""

colour_map = {}
for _line in _colour_map_text.splitlines():
    _name, _num = _line.split()
    _num = int(_num, 0)
    colour_map[_name] = _num
    if 'gray' in _name:
        colour_map[_name.replace('gray', 'grey')] = _num
del _colour_map_text, _line, _name, _num


pattern_map = {
    # Text values for pattern.pattern
    # xlwt/doc/pattern_examples.xls showcases all of these patterns.
    'no_fill':              0,
    'none':                 0,
    'solid':                1,
    'solid_fill':           1,
    'solid_pattern':        1,
    'fine_dots':            2,
    'alt_bars':             3,
    'sparse_dots':          4,
    'thick_horz_bands':     5,
    'thick_vert_bands':     6,
    'thick_backward_diag':  7,
    'thick_forward_diag':   8,
    'big_spots':            9,
    'bricks':               10,
    'thin_horz_bands':      11,
    'thin_vert_bands':      12,
    'thin_backward_diag':   13,
    'thin_forward_diag':    14,
    'squares':              15,
    'diamonds':             16,
    }

def any_str_func(s):
    return s.strip()

def colour_index_func(s, maxval=0x7F):
    try:
        value = int(s, 0)
    except ValueError:
        return None
    if not (0 <= value <= maxval):
        return None
    return value

colour_index_func_7 = colour_index_func

def colour_index_func_15(s):
    return colour_index_func(s, maxval=0x7FFF)

def rotation_func(s):
    try:
        value = int(s, 0)
    except ValueError:
        return None
    if not (-90 <= value <= 90):
        raise EasyXFCallerError("rotation %d: should be -90 to +90 degrees" % value)
    if value < 0:
        value = 90 - value # encode as 91 to 180 (clockwise)
    return value

xf_dict = {
    'align': 'alignment', # synonym
    'alignment': {
        'dire': {
            'general': 0,
            'lr': 1,
            'rl': 2,
            },
        'direction': 'dire',
        'horiz': 'horz',
        'horizontal': 'horz',
        'horz': {
            'general': 0,
            'left': 1,
            'center': 2,
            'centre': 2, # "align: horiz centre" means xf.alignment.horz is set to 2
            'right': 3,
            'filled': 4,
            'justified': 5,
            'center_across_selection': 6,
            'centre_across_selection': 6,
            'distributed': 7,
            },
        'inde': IntULim(15), # restriction: 0 <= value <= 15
        'indent': 'inde',
        'rota': [{'stacked': 255, 'none': 0, }, rotation_func],
        'rotation': 'rota',
        'shri': bool_map,
        'shrink': 'shri',
        'shrink_to_fit': 'shri',
        'vert': {
            'top': 0,
            'center': 1,
            'centre': 1,
            'bottom': 2,
            'justified': 3,
            'distributed': 4,
            },
         'vertical': 'vert',
         'wrap': bool_map,
         },
    'border': 'borders',
    'borders': {
        'left':     [border_line_map, IntULim(0x0d)],
        'right':    [border_line_map, IntULim(0x0d)],
        'top':      [border_line_map, IntULim(0x0d)],
        'bottom':   [border_line_map, IntULim(0x0d)],
        'diag':     [border_line_map, IntULim(0x0d)],
        'top_colour':       [colour_map, colour_index_func_7],
        'bottom_colour':    [colour_map, colour_index_func_7],
        'left_colour':      [colour_map, colour_index_func_7],
        'right_colour':     [colour_map, colour_index_func_7],
        'diag_colour':      [colour_map, colour_index_func_7],
        'top_color':        'top_colour',
        'bottom_color':     'bottom_colour',
        'left_color':       'left_colour',
        'right_color':      'right_colour',
        'diag_color':       'diag-colour',
        'need_diag_1':  bool_map,
        'need_diag_2':  bool_map,
        },
    'font': {
        'bold': bool_map,
        'charset': charset_map,
        'color':  'colour_index',
        'color_index':  'colour_index',
        'colour':  'colour_index',
        'colour_index': [colour_map, colour_index_func_15],
        'escapement': {'none': 0, 'superscript': 1, 'subscript': 2},
        'family': {'none': 0, 'roman': 1, 'swiss': 2, 'modern': 3, 'script': 4, 'decorative': 5, },
        'height': IntULim(0xFFFF), # practical limits are much narrower e.g. 160 to 1440 (8pt to 72pt)
        'italic': bool_map,
        'name': any_str_func,
        'outline': bool_map,
        'shadow': bool_map,
        'struck_out': bool_map,
        'underline': [bool_map, {'none': 0, 'single': 1, 'single_acc': 0x21, 'double': 2, 'double_acc': 0x22, }],
        },
    'pattern': {
        'back_color':   'pattern_back_colour',
        'back_colour':  'pattern_back_colour',
        'fore_color':   'pattern_fore_colour',
        'fore_colour':  'pattern_fore_colour',
        'pattern': [pattern_map, IntULim(16)],
        'pattern_back_color':   'pattern_back_colour',
        'pattern_back_colour':  [colour_map, colour_index_func_7],
        'pattern_fore_color':   'pattern_fore_colour',
        'pattern_fore_colour':  [colour_map, colour_index_func_7],
        },
    'protection': {
        'cell_locked' :   bool_map,
        'formula_hidden': bool_map,
        },
    }

def _esplit(s, split_char, esc_char="\\"):
    escaped = False
    olist = ['']
    for c in s:
        if escaped:
            olist[-1] += c
            escaped = False
        elif c == esc_char:
            escaped = True
        elif c == split_char:
            olist.append('')
        else:
            olist[-1] += c
    return olist

def _parse_strg_to_obj(strg, obj, parse_dict,
    field_sep=",", line_sep=";", intro_sep=":", esc_char="\\", debug=False):
    for line in _esplit(strg, line_sep, esc_char):
        line = line.strip()
        if not line:
            break
        split_line = _esplit(line, intro_sep, esc_char)
        if len(split_line) != 2:
            raise EasyXFCallerError('line %r should have exactly 1 "%c"' % (line, intro_sep))
        section, item_str = split_line
        section = section.strip().lower()
        for counter in range(2):
            result = parse_dict.get(section)
            if result is None:
                raise EasyXFCallerError('section %r is unknown' % section)
            if isinstance(result, dict):
                break
            if not isinstance(result, str):
                raise EasyXFAuthorError(
                    'section %r should map to dict or str object; found %r' % (section, type(result)))
            # synonym
            old_section = section
            section = result
        else:
            raise EasyXFAuthorError('Attempt to define synonym of synonym (%r: %r)' % (old_section, result))
        section_dict = result
        section_obj = getattr(obj, section, None)
        if section_obj is None:
            raise EasyXFAuthorError('instance of %s class has no attribute named %s' % (obj.__class__.__name__, section))
        for kv_str in _esplit(item_str, field_sep, esc_char):
            guff = kv_str.split()
            if not guff:
                continue
            k = guff[0].lower().replace('-', '_')
            v = ' '.join(guff[1:])
            if not v:
                raise EasyXFCallerError("no value supplied for %s.%s" % (section, k))
            for counter in xrange(2):
                result = section_dict.get(k)
                if result is None:
                    raise EasyXFCallerError('%s.%s is not a known attribute' % (section, k))
                if not isinstance(result, basestring):
                    break
                # synonym
                old_k = k
                k = result
            else:
                raise EasyXFAuthorError('Attempt to define synonym of synonym (%r: %r)' % (old_k, result))
            value_info = result
            if not isinstance(value_info, list):
                value_info = [value_info]
            for value_rule in value_info:
                if isinstance(value_rule, dict):
                    # dict maps strings to integer field values
                    vl = v.lower().replace('-', '_')
                    if vl in value_rule:
                        value = value_rule[vl]
                        break
                elif callable(value_rule):
                    value = value_rule(v)
                    if value is not None:
                        break
                else:
                    raise EasyXFAuthorError("unknown value rule for attribute %r: %r" % (k, value_rule))
            else:
                raise EasyXFCallerError("unexpected value %r for %s.%s" % (v, section, k))
            try:
                orig = getattr(section_obj, k)
            except AttributeError:
                raise EasyXFAuthorError('%s.%s in dictionary but not in supplied object' % (section, k))
            if debug: print "+++ %s.%s = %r # %s; was %r" % (section, k, value, v, orig)
            setattr(section_obj, k, value)

def easyxf(strg_to_parse="", num_format_str=None,
    field_sep=",", line_sep=";", intro_sep=":", esc_char="\\", debug=False):
    xfobj = XFStyle()
    if num_format_str is not None:
        xfobj.num_format_str = num_format_str
    if strg_to_parse:
        _parse_strg_to_obj(strg_to_parse, xfobj, xf_dict,
            field_sep=field_sep, line_sep=line_sep, intro_sep=intro_sep, esc_char=esc_char, debug=debug)
    return xfobj
