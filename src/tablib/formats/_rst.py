# -*- coding: utf-8 -*-

""" Tablib - reStructuredText Support
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from textwrap import TextWrapper

from tablib.compat import (
    median,
    unicode,
    izip_longest,
)


title = 'rst'
extensions = ('rst',)


MAX_TABLE_WIDTH = 80  # Roughly. It may be wider to avoid breaking words.


JUSTIFY_LEFT = 'left'
JUSTIFY_CENTER = 'center'
JUSTIFY_RIGHT = 'right'
JUSTIFY_VALUES = (JUSTIFY_LEFT, JUSTIFY_CENTER, JUSTIFY_RIGHT)


def to_unicode(value):
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return unicode(value)


def _max_word_len(text):
    """
    Return the length of the longest word in `text`.


    >>> _max_word_len('Python Module for Tabular Datasets')
    8

    """
    return max((len(word) for word in text.split()))


def _get_column_string_lengths(dataset):
    """
    Returns a list of string lengths of each column, and a list of
    maximum word lengths.
    """
    if dataset.headers:
        column_lengths = [[len(h)] for h in dataset.headers]
        word_lens = [_max_word_len(h) for h in dataset.headers]
    else:
        column_lengths = [[] for _ in range(dataset.width)]
        word_lens = [0 for _ in range(dataset.width)]
    for row in dataset.dict:
        values = iter(row.values() if hasattr(row, 'values') else row)
        for i, val in enumerate(values):
            text = to_unicode(val)
            column_lengths[i].append(len(text))
            word_lens[i] = max(word_lens[i], _max_word_len(text))
    return column_lengths, word_lens


def _row_to_lines(values, widths, wrapper, sep='|', justify=JUSTIFY_LEFT):
    """
    Returns a table row of wrapped values as a list of lines
    """
    if justify not in JUSTIFY_VALUES:
        raise ValueError('Value of "justify" must be one of "{}"'.format(
            '", "'.join(JUSTIFY_VALUES)
        ))
    if justify == JUSTIFY_LEFT:
        just = lambda text, width: text.ljust(width)
    elif justify == JUSTIFY_CENTER:
        just = lambda text, width: text.center(width)
    else:
        just = lambda text, width: text.rjust(width)
    lpad = sep + ' ' if sep else ''
    rpad = ' ' + sep if sep else ''
    pad = ' ' + sep + ' '
    cells = []
    for value, width in zip(values, widths):
        wrapper.width = width
        text = to_unicode(value)
        cell = wrapper.wrap(text)
        cells.append(cell)
    lines = izip_longest(*cells, fillvalue='')
    lines = (
        (just(cell_line, widths[i]) for i, cell_line in enumerate(line))
        for line in lines
    )
    lines = [''.join((lpad, pad.join(line), rpad)) for line in lines]
    return lines


def _get_column_widths(dataset, max_table_width=MAX_TABLE_WIDTH, pad_len=3):
    """
    Returns a list of column widths proportional to the median length
    of the text in their cells.
    """
    str_lens, word_lens = _get_column_string_lengths(dataset)
    median_lens = [int(median(lens)) for lens in str_lens]
    total = sum(median_lens)
    if total > max_table_width - (pad_len * len(median_lens)):
        column_widths = (max_table_width * l // total for l in median_lens)
    else:
        column_widths = (l for l in median_lens)
    # Allow for separator and padding:
    column_widths = (w - pad_len if w > pad_len else w for w in column_widths)
    # Rather widen table than break words:
    column_widths = [max(w, l) for w, l in zip(column_widths, word_lens)]
    return column_widths


def export_set_as_simple_table(dataset, column_widths=None):
    """
    Returns reStructuredText grid table representation of dataset.
    """
    lines = []
    wrapper = TextWrapper()
    if column_widths is None:
        column_widths = _get_column_widths(dataset, pad_len=2)
    border = '  '.join(['=' * w for w in column_widths])

    lines.append(border)
    if dataset.headers:
        lines.extend(_row_to_lines(
            dataset.headers,
            column_widths,
            wrapper,
            sep='',
            justify=JUSTIFY_CENTER,
        ))
        lines.append(border)
    for row in dataset.dict:
        values = iter(row.values() if hasattr(row, 'values') else row)
        lines.extend(_row_to_lines(values, column_widths, wrapper, ''))
    lines.append(border)
    return '\n'.join(lines)


def export_set_as_grid_table(dataset, column_widths=None):
    """
    Returns reStructuredText grid table representation of dataset.


    >>> from tablib import Dataset
    >>> from tablib.formats import rst
    >>> bits = ((0, 0), (1, 0), (0, 1), (1, 1))
    >>> data = Dataset()
    >>> data.headers = ['A', 'B', 'A and B']
    >>> for a, b in bits:
    ...     data.append([bool(a), bool(b), bool(a * b)])
    >>> print(rst.export_set(data, force_grid=True))
    +-------+-------+-------+
    |   A   |   B   | A and |
    |       |       |   B   |
    +=======+=======+=======+
    | False | False | False |
    +-------+-------+-------+
    | True  | False | False |
    +-------+-------+-------+
    | False | True  | False |
    +-------+-------+-------+
    | True  | True  | True  |
    +-------+-------+-------+

    """
    lines = []
    wrapper = TextWrapper()
    if column_widths is None:
        column_widths = _get_column_widths(dataset)
    header_sep = '+=' + '=+='.join(['=' * w for w in column_widths]) + '=+'
    row_sep = '+-' + '-+-'.join(['-' * w for w in column_widths]) + '-+'

    lines.append(row_sep)
    if dataset.headers:
        lines.extend(_row_to_lines(
            dataset.headers,
            column_widths,
            wrapper,
            justify=JUSTIFY_CENTER,
        ))
        lines.append(header_sep)
    for row in dataset.dict:
        values = iter(row.values() if hasattr(row, 'values') else row)
        lines.extend(_row_to_lines(values, column_widths, wrapper))
        lines.append(row_sep)
    return '\n'.join(lines)


def _use_simple_table(head0, col0, width0):
    """
    Use a simple table if the text in the first column is never wrapped


    >>> _use_simple_table('menu', ['egg', 'bacon'], 10)
    True
    >>> _use_simple_table(None, ['lobster thermidor', 'spam'], 10)
    False

    """
    if head0 is not None:
        head0 = to_unicode(head0)
        if len(head0) > width0:
            return False
    for cell in col0:
        cell = to_unicode(cell)
        if len(cell) > width0:
            return False
    return True


def export_set(dataset, **kwargs):
    """
    Returns reStructuredText table representation of dataset.

    Returns a simple table if the text in the first column is never
    wrapped, otherwise returns a grid table.


    >>> from tablib import Dataset
    >>> bits = ((0, 0), (1, 0), (0, 1), (1, 1))
    >>> data = Dataset()
    >>> data.headers = ['A', 'B', 'A and B']
    >>> for a, b in bits:
    ...     data.append([bool(a), bool(b), bool(a * b)])
    >>> table = data.rst
    >>> table.split('\\n') == [
    ...     '=====  =====  =====',
    ...     '  A      B    A and',
    ...     '                B  ',
    ...     '=====  =====  =====',
    ...     'False  False  False',
    ...     'True   False  False',
    ...     'False  True   False',
    ...     'True   True   True ',
    ...     '=====  =====  =====',
    ... ]
    True

    """
    if not dataset.dict:
        return ''
    force_grid = kwargs.get('force_grid', False)
    max_table_width = kwargs.get('max_table_width', MAX_TABLE_WIDTH)
    column_widths = _get_column_widths(dataset, max_table_width)

    use_simple_table = _use_simple_table(
        dataset.headers[0] if dataset.headers else None,
        dataset.get_col(0),
        column_widths[0],
    )
    if use_simple_table and not force_grid:
        return export_set_as_simple_table(dataset, column_widths)
    else:
        return export_set_as_grid_table(dataset, column_widths)


def export_book(databook):
    """
    reStructuredText representation of a Databook.

    Tables are separated by a blank line. All tables use the grid
    format.
    """
    return '\n\n'.join(export_set(dataset, force_grid=True)
                       for dataset in databook._datasets)
