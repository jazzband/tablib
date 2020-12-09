class TablibException(Exception):
    """Tablib common exception."""


class InvalidDatasetType(TablibException, TypeError):
    """Only Datasets can be added to a DataBook."""


class InvalidDimensions(TablibException, ValueError):
    """Invalid size."""


class InvalidDatasetIndex(TablibException, IndexError):
    """Outside of Dataset size."""


class HeadersNeeded(TablibException, AttributeError):
    """Header parameter must be given when appending a column in this Dataset."""


class UnsupportedFormat(TablibException, NotImplementedError):
    """Format is not supported."""
