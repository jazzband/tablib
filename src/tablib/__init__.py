""" Tablib. """
from pkg_resources import DistributionNotFound, get_distribution
from tablib.core import (  # noqa: F401
    Databook,
    Dataset,
    InvalidDatasetType,
    InvalidDimensions,
    UnsupportedFormat,
    detect_format,
    import_book,
    import_set,
)

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = None
