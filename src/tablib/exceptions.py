class InvalidDatasetType(Exception):
    "Only Datasets can be added to a DataBook"


class InvalidDimensions(Exception):
    "Invalid size"


class InvalidDatasetIndex(Exception):
    "Outside of Dataset size"


class HeadersNeeded(Exception):
    "Header parameter must be given when appending a column in this Dataset."


class UnsupportedFormat(NotImplementedError):
    "Format is not supported"
