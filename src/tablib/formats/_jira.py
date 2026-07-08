"""Tablib - Jira table export support.

   Generates a Jira table from the dataset.
"""


class JIRAFormat:
    title = 'jira'

    @classmethod
    def export_set(cls, dataset):
        """Formats the dataset according to the Jira table syntax:

        ||heading 1||heading 2||heading 3||
        |col A1|col A2|col A3|
        |col B1|col B2|col B3|

        :param dataset: dataset to serialize
        :type dataset: tablib.core.Dataset
        """

        header = cls._get_header(dataset.headers) if dataset.headers else ''
        body = cls._get_body(dataset)
        return f'{header}\n{body}' if header else body

    @classmethod
    def _get_body(cls, dataset):
        return '\n'.join([cls._serialize_row(row) for row in dataset])

    @classmethod
    def _get_header(cls, headers):
        return cls._serialize_row(headers, delimiter='||')

    @classmethod
    def _serialize_row(cls, row, delimiter='|'):
        return '{}{}{}'.format(
            delimiter,
            delimiter.join([' ' if cls._is_empty_value(item) else str(item) for item in row]),
            delimiter
        )

    @classmethod
    def _is_empty_value(cls, item):
        if item is None:
            return True
        if isinstance(item, (str, bytes, bytearray)):
            return len(item) == 0
        if isinstance(item, (list, tuple, dict, set, frozenset)):
            return len(item) == 0
        return False
