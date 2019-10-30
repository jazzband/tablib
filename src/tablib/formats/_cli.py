""" Tablib - CLI Support
"""
from tabulate import tabulate

title = 'cli'
extensions = ('txt',)

DEFAULT_FORMAT = 'plain'

def export_set(dataset, **kwargs):
    """Returns CLI representation of Dataset."""
    if( dataset.headers is not None ): 
        kwargs.setdefault('headers', dataset.headers)
    kwargs.setdefault('tablefmt', DEFAULT_FORMAT)
    return tabulate( dataset, **kwargs)

