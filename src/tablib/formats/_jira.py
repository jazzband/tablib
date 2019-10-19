"""Tablib - Jira table export support.

   Generates a Jira table from the dataset.
"""

title = 'jira'


def export_set(dataset):
    """Formats the dataset according to the Jira table syntax:

    ||heading 1||heading 2||heading 3||
    |col A1|col A2|col A3|
    |col B1|col B2|col B3|

    :param dataset: dataset to serialize
    :type dataset: tablib.core.Dataset
    """

    header = _get_header(dataset.headers) if dataset.headers else ''
    body = _get_body(dataset)
    return '{}\n{}'.format(header, body) if header else body


def _get_body(dataset):
    return '\n'.join([_serialize_row(row) for row in dataset])


def _get_header(headers):
    return _serialize_row(headers, delimiter='||')


def _serialize_row(row, delimiter='|'):
    return '{}{}{}'.format(delimiter,
                           delimiter.join([str(item) if item else ' ' for item in row]),
                           delimiter)
