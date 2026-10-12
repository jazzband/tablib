__lazy_modules__ = {"io"}

from io import BytesIO, StringIO


def is_empty_cell(value):
    return (
        value is None
        or (
            isinstance(value, (str, bytes, bytearray, list, tuple, dict, set, frozenset))
            and len(value) == 0
        )
    )


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
