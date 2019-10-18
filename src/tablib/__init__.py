""" Tablib. """
from pkg_resources import get_distribution, DistributionNotFound

from tablib.core import (
    Databook, Dataset, detect_format, import_set, import_book,
    InvalidDatasetType, InvalidDimensions, UnsupportedFormat
)

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = None
