# -*- coding: utf-8 -*-

""" Tablib - CSV Support.
"""

import sys
if sys.version_info[0] > 2:
    from io import StringIO
else:
    from cStringIO import StringIO


import csv
import os

import tablib


title = 'csv'
extentions = ('csv',)



def export_set(dataset):
    """Returns CSV representation of Dataset."""
    stream = StringIO()
    _csv = csv.writer(stream)

    for row in dataset._package(dicts=False):
        _csv.writerow(row)

    return stream.getvalue()


def import_set(dset, in_stream, headers=True):
    """Returns dataset from CSV stream."""

    dset.wipe()

    rows = csv.reader(in_stream.splitlines())
    for i, row in enumerate(rows):

        if (i == 0) and (headers):
            dset.headers = row
        else:
            dset.append(row)


def detect(stream):
    """Returns True if given stream is valid CSV."""
    try:
        rows = dialect = csv.Sniffer().sniff(stream)
        return True
    except csv.Error:
        return False