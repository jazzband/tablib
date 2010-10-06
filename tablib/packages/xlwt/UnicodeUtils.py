# -*- coding: windows-1252 -*-

'''
From BIFF8 on, strings are always stored using UTF-16LE  text encoding. The
character  array  is  a  sequence  of  16-bit  values4.  Additionally it is
possible  to  use  a  compressed  format, which omits the high bytes of all
characters, if they are all zero.

The following tables describe the standard format of the entire string, but
in many records the strings differ from this format. This will be mentioned
separately. It is possible (but not required) to store Rich-Text formatting
information  and  Asian  phonetic information inside a Unicode string. This
results  in  four  different  ways  to  store a string. The character array
is not zero-terminated.

The  string  consists  of  the  character count (as usual an 8-bit value or
a  16-bit value), option flags, the character array and optional formatting
information.  If the string is empty, sometimes the option flags field will
not occur. This is mentioned at the respective place.

Offset  Size    Contents
0       1 or 2  Length of the string (character count, ln)
1 or 2  1       Option flags:
                  Bit   Mask Contents
                  0     01H  Character compression (ccompr):
                               0 = Compressed (8-bit characters)
                               1 = Uncompressed (16-bit characters)
                  2     04H  Asian phonetic settings (phonetic):
                               0 = Does not contain Asian phonetic settings
                               1 = Contains Asian phonetic settings
                  3     08H  Rich-Text settings (richtext):
                               0 = Does not contain Rich-Text settings
                               1 = Contains Rich-Text settings
[2 or 3] 2      (optional, only if richtext=1) Number of Rich-Text formatting runs (rt)
[var.]   4      (optional, only if phonetic=1) Size of Asian phonetic settings block (in bytes, sz)
var.     ln or 
         2·ln   Character array (8-bit characters or 16-bit characters, dependent on ccompr)
[var.]   4·rt   (optional, only if richtext=1) List of rt formatting runs 
[var.]   sz     (optional, only if phonetic=1) Asian Phonetic Settings Block 
'''


from struct import pack

def upack2(s, encoding='ascii'):
    # If not unicode, make it so.
    if isinstance(s, unicode):
        us = s
    else:
        us = unicode(s, encoding)
    # Limit is based on number of content characters
    # (not on number of bytes in packed result)
    len_us = len(us)
    if len_us > 65535:
        raise Exception('String longer than 65535 characters')
    try:
        encs = us.encode('latin1')
        # Success here means all chars are in U+0000 to U+00FF
        # inclusive, meaning that we can use "compressed format".
        flag = 0
    except UnicodeEncodeError:
        encs = us.encode('utf_16_le')
        flag = 1
    return pack('<HB', len_us, flag) + encs

def upack1(s, encoding='ascii'):
    # Same as upack2(), but with a one-byte length field.
    if isinstance(s, unicode):
        us = s
    else:
        us = unicode(s, encoding)
    len_us = len(us)
    if len_us > 255:
        raise Exception('String longer than 255 characters')
    try:
        encs = us.encode('latin1')
        flag = 0
    except UnicodeEncodeError:
        encs = us.encode('utf_16_le')
        flag = 1
    return pack('<BB', len_us, flag) + encs
