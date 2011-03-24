""" Tablib.
"""

import sys
if sys.version_info[0:1] > (2, 5):
    from tablib.core import (
        Databook, Dataset, detect, import_set, 
        InvalidDatasetType, InvalidDimensions, UnsupportedFormat
    )
    
else:
    from tablib.core25 import (
        Databook, Dataset, detect, import_set, 
        InvalidDatasetType, InvalidDimensions, UnsupportedFormat
    )

