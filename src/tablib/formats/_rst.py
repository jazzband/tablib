""" Tablib - reStructuredText Support
"""

__lazy_modules__ = {"itertools", "statistics", "textwrap"}

from itertools import zip_longest
from statistics import median
from textwrap import TextWrapper

JUSTIFY_LEFT = 'left'
JUSTIFY_CENTER = 'center'
JUSTIFY_RIGHT = 'right'
JUSTIFY_VALUES = (JUSTIFY_LEFT, JUSTIFY_CENTER, JUSTIFY_RIGHT)

# The characters TextWrapper treats as whitespace. A cell containing none of
# them, and already short enough for its column, is returned unchanged by the
# wrapper, so it can be turned into a line directly.
_WHITESPACE = frozenset('\t\n\x0b\x0c\r ')


def to_str(value):
    if value.__class__ is str:
        return value
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return str(value)


def _max_word_len(text):
    """
    Return the length of the longest word in `text`.

    >>> _max_word_len('Python Module for Tabular Datasets')
    8
    """
    return max((len(word) for word in text.split()), default=0) if text else 0


class ReSTFormat:
    title = 'rst'
    extensions = ('rst',)

    MAX_TABLE_WIDTH = 80  # Roughly. It may be wider to avoid breaking words.

    @classmethod
    def _prepare(cls, dataset):
        """
        Returns the headers and rows as strings, packaged once.

        ``dataset.dict`` rebuilds the whole dataset on every access, and when
        headers are set it allocates a dict per row that every caller here
        immediately discards again via ``row.values()``. Converting the cells
        once and passing the strings on also avoids running ``to_str`` over
        every cell a second time when the rows are rendered.
        """
        rows = dataset._package(dicts=False)
        headers = dataset.headers
        if not headers:
            return None, [[to_str(cell) for cell in row] for row in rows]

        rows = rows[1:]
        if len(set(headers)) != len(headers):
            # ``dataset.dict`` routes each row through dict(zip(headers, row)),
            # so a repeated header name keeps only the last column carrying it,
            # ordered by first occurrence. Resolve those positions once instead
            # of rebuilding a dict per row. The header row itself is not
            # narrowed, matching what dataset.dict leaves the callers with.
            keep = {}
            for index, header in enumerate(headers):
                keep[header] = index
            indexes = list(keep.values())
            rows = [[to_str(row[i]) for i in indexes] for row in rows]
        else:
            rows = [[to_str(cell) for cell in row] for row in rows]
        return [to_str(header) for header in headers], rows

    @classmethod
    def _get_column_string_lengths(cls, str_headers, str_rows, width):
        """
        Returns a list of string lengths of each column, and a list of
        maximum word lengths.
        """
        if str_headers:
            column_lengths = [[len(h)] for h in str_headers]
            word_lens = [_max_word_len(h) for h in str_headers]
        else:
            column_lengths = [[] for _ in range(width)]
            word_lens = [0 for _ in range(width)]
        for row in str_rows:
            for i, text in enumerate(row):
                text_len = len(text)
                column_lengths[i].append(text_len)
                # No word can be longer than the cell holding it, so a cell no
                # longer than the running maximum cannot raise it.
                if text_len > word_lens[i]:
                    if _WHITESPACE.isdisjoint(text):
                        word_lens[i] = text_len
                    else:
                        word_len = _max_word_len(text)
                        if word_len > word_lens[i]:
                            word_lens[i] = word_len
        return column_lengths, word_lens

    @classmethod
    def _row_to_lines(cls, values, widths, wrapper, sep='|', justify=JUSTIFY_LEFT):
        """
        Returns a table row of wrapped values as a list of lines
        """
        if justify not in JUSTIFY_VALUES:
            raise ValueError('Value of "justify" must be one of "{}"'.format(
                '", "'.join(JUSTIFY_VALUES)
            ))

        # Pick the padding method once rather than re-testing `justify` inside
        # a closure for every cell of every row.
        if justify == JUSTIFY_LEFT:
            just = str.ljust
        elif justify == JUSTIFY_CENTER:
            just = str.center
        else:
            just = str.rjust
        lpad = sep + ' ' if sep else ''
        rpad = ' ' + sep if sep else ''
        pad = ' ' + sep + ' '
        cells = []
        for value, width in zip(values, widths):
            text = to_str(value)
            # A non-empty cell holding no whitespace and already fitting its
            # column comes back from the wrapper unchanged. Widths of zero or
            # less are left to TextWrapper, which rejects them.
            if 0 < len(text) <= width and _WHITESPACE.isdisjoint(text):
                cells.append([text])
            else:
                wrapper.width = width
                cells.append(wrapper.wrap(text))
        return [
            ''.join((
                lpad,
                pad.join([just(cell_line, widths[i])
                          for i, cell_line in enumerate(line)]),
                rpad,
            ))
            for line in zip_longest(*cells, fillvalue='')
        ]

    @classmethod
    def _get_column_widths(cls, dataset, max_table_width=MAX_TABLE_WIDTH, pad_len=3,
                           prepared=None):
        """
        Returns a list of column widths proportional to the median length
        of the text in their cells.
        """
        if prepared is None:
            prepared = cls._prepare(dataset)
        str_headers, str_rows = prepared
        str_lens, word_lens = cls._get_column_string_lengths(
            str_headers, str_rows, dataset.width
        )
        median_lens = [int(median(lens)) for lens in str_lens]
        total = sum(median_lens)
        if total > max_table_width - (pad_len * len(median_lens)):
            column_widths = (max_table_width * lens // total for lens in median_lens)
        else:
            column_widths = (lens for lens in median_lens)
        # Allow for separator and padding:
        column_widths = (w - pad_len if w > pad_len else w for w in column_widths)
        # Rather widen table than break words:
        column_widths = [max(w, l) for w, l in zip(column_widths, word_lens)]
        return column_widths

    @classmethod
    def export_set_as_simple_table(cls, dataset, column_widths=None, prepared=None):
        """
        Returns reStructuredText grid table representation of dataset.
        """
        if prepared is None:
            prepared = cls._prepare(dataset)
        str_headers, str_rows = prepared
        lines = []
        wrapper = TextWrapper()
        if column_widths is None:
            column_widths = cls._get_column_widths(dataset, pad_len=2, prepared=prepared)
        border = '  '.join(['=' * w for w in column_widths])

        lines.append(border)
        if str_headers:
            lines.extend(cls._row_to_lines(
                str_headers,
                column_widths,
                wrapper,
                sep='',
                justify=JUSTIFY_CENTER,
            ))
            lines.append(border)
        for row in str_rows:
            lines.extend(cls._row_to_lines(row, column_widths, wrapper, ''))
        lines.append(border)
        return '\n'.join(lines)

    @classmethod
    def export_set_as_grid_table(cls, dataset, column_widths=None, prepared=None):
        """
        Returns reStructuredText grid table representation of dataset.


        >>> from tablib import Dataset
        >>> from tablib.formats import registry
        >>> bits = ((0, 0), (1, 0), (0, 1), (1, 1))
        >>> data = Dataset()
        >>> data.headers = ['A', 'B', 'A and B']
        >>> for a, b in bits:
        ...     data.append([bool(a), bool(b), bool(a * b)])
        >>> rst = registry.get_format('rst')
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
        if prepared is None:
            prepared = cls._prepare(dataset)
        str_headers, str_rows = prepared
        lines = []
        wrapper = TextWrapper()
        if column_widths is None:
            column_widths = cls._get_column_widths(dataset, prepared=prepared)
        header_sep = '+=' + '=+='.join(['=' * w for w in column_widths]) + '=+'
        row_sep = '+-' + '-+-'.join(['-' * w for w in column_widths]) + '-+'

        lines.append(row_sep)

        if str_headers:
            lines.extend(cls._row_to_lines(
                str_headers,
                column_widths,
                wrapper,
                justify=JUSTIFY_CENTER,
            ))
            lines.append(header_sep)
        for row in str_rows:
            lines.extend(cls._row_to_lines(row, column_widths, wrapper))
            lines.append(row_sep)
        return '\n'.join(lines)

    @classmethod
    def _use_simple_table(cls, head0, col0, width0):
        """
        Use a simple table if the text in the first column is never wrapped


        >>> from tablib.formats import registry
        >>> rst = registry.get_format('rst')
        >>> rst._use_simple_table('menu', ['egg', 'bacon'], 10)
        True
        >>> rst._use_simple_table(None, ['lobster thermidor', 'spam'], 10)
        False

        """
        if head0 is not None:
            head0 = to_str(head0)
            if len(head0) > width0:
                return False
        for cell in col0:
            cell = to_str(cell)
            if len(cell) > width0:
                return False
        return True

    @classmethod
    def export_set(cls, dataset, **kwargs):
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
        prepared = cls._prepare(dataset)
        if not prepared[1]:
            return ''
        force_grid = kwargs.get('force_grid', False)
        max_table_width = kwargs.get('max_table_width', cls.MAX_TABLE_WIDTH)
        column_widths = cls._get_column_widths(dataset, max_table_width,
                                               prepared=prepared)

        use_simple_table = cls._use_simple_table(
            dataset.headers[0] if dataset.headers else None,
            dataset.get_col(0),
            column_widths[0],
        )
        if use_simple_table and not force_grid:
            return cls.export_set_as_simple_table(dataset, column_widths, prepared)
        else:
            return cls.export_set_as_grid_table(dataset, column_widths, prepared)

    @classmethod
    def export_book(cls, databook):
        """
        reStructuredText representation of a Databook.

        Tables are separated by a blank line. All tables use the grid
        format.
        """
        return '\n\n'.join(cls.export_set(dataset, force_grid=True)
                           for dataset in databook._datasets)
