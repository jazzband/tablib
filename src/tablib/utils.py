__lazy_modules__ = {"io"}

from io import BytesIO, StringIO

# The largest (and, by symmetry, smallest) integer magnitude that can be
# represented exactly as an IEEE-754 double, which is how spreadsheet
# formats such as XLS and XLSX store numeric cell values internally.
MAX_EXACT_INT_IN_DOUBLE = 2 ** 53


def normalize_input(stream):
    """
    Accept either a str/bytes stream or a file-like object and always return a
    file-like object.
    """
    if isinstance(stream, str):
        return StringIO(stream, newline='')
    elif isinstance(stream, bytes):
        return BytesIO(stream)
    return stream


def spreadsheet_safe_value(value):
    """
    Return ``value`` unchanged, unless it's an ``int`` too large to be
    represented exactly as an IEEE-754 double -- the numeric storage used
    internally by spreadsheet formats like XLS and XLSX. In that case,
    return the value's exact decimal string representation instead, so
    that writing it to a spreadsheet doesn't silently corrupt it into a
    nearby, incorrect number.

    ``bool`` is intentionally excluded, since it's a subclass of ``int``
    but should keep its normal boolean handling.
    """
    if (
        isinstance(value, int)
        and not isinstance(value, bool)
        and abs(value) > MAX_EXACT_INT_IN_DOUBLE
    ):
        return str(value)
    return value
