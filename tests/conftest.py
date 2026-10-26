"""Make the ``tablib`` package importable without an install.

Tries, in order: this workdir's ``tablib-src/src`` checkout and the
repo root's ``src`` layout (the layout the PR targets).
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = (
    os.path.join(_HERE, "..", "tablib-src", "src"),
    os.path.join(_HERE, "..", "..", "src"),
)
for _candidate in _CANDIDATES:
    if os.path.isdir(os.path.join(_candidate, "tablib")):
        sys.path.insert(0, os.path.normpath(_candidate))
