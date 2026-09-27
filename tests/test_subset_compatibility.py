from copy import copy

import pytest

from tablib import Dataset
from tablib.core import Row


def original_subset(dataset, rows=None, cols=None):
    if not dataset:
        return
    if rows is None:
        rows = list(range(dataset.height))
    if cols is None:
        cols = list(dataset.headers)
    rows = [row for row in rows if row in range(dataset.height)]
    cols = [header for header in cols if header in dataset.headers]
    result = Dataset()
    result.headers = list(cols)
    result._data = []
    for row_no, row in enumerate(dataset._data):
        data_row = []
        for header in result.headers:
            if header in dataset.headers:
                data_row.append(row[dataset.headers.index(header)])
            else:
                raise KeyError
        if row_no in rows:
            result.append(row=Row(data_row))
    return result


@pytest.mark.parametrize('rows', [None, [], [0]])
def test_subset_selector_changing_headers_keeps_key_error(rows):
    dataset = Dataset(['Synthetic A', 20], ['Synthetic B', 30], headers=['name', 'age'])

    def columns():
        yield 'name'
        dataset.headers = ['renamed', 'age']

    with pytest.raises(KeyError) as error:
        dataset.subset(rows=rows, cols=columns())
    assert error.value.args == ()
    assert error.value.__cause__ is None
    assert error.value.__context__ is None


@pytest.mark.parametrize('rows', [None, [], [0]])
@pytest.mark.parametrize('at,raises', [(2, False), (4, False), (2, True), (3, True), (4, True)])
def test_subset_preserves_stateful_comparisons_and_their_errors(rows, at, raises):
    def run(method):
        calls = []

        class Column(str):
            def __eq__(self, other):
                calls.append(other)
                if len(calls) == at:
                    if raises:
                        raise ValueError('custom comparison error')
                    return False
                return super().__eq__(other)

        dataset = Dataset(['Synthetic A'], ['Synthetic B'], headers=['name'])
        try:
            result = method(dataset, rows=rows, cols=[Column('name')])
            outcome = list(result)
        except (KeyError, ValueError) as error:
            outcome = type(error), error.args
        return outcome, calls

    assert run(Dataset.subset) == run(original_subset)


@pytest.mark.parametrize('headers,columns', [
    ([1, 2], [2, 1]),
    ([None, 'age'], [None]),
    (['name', 'name'], ['name', 'name']),
    (['name', 'age'], ['missing', 'name', 'name']),
])
def test_subset_nonstring_and_duplicate_headers_match_original(headers, columns):
    dataset = Dataset(['Synthetic A', 20], ['Synthetic B', 30], headers=headers)
    expected = original_subset(dataset, cols=columns)
    actual = dataset.subset(cols=columns)
    assert actual.headers == expected.headers
    assert list(actual) == list(expected)


def test_subset_subclass_keeps_header_access_behavior():
    class ObservedDataset(Dataset):
        def __init__(self, *args, **kwargs):
            self.header_reads = 0
            super().__init__(*args, **kwargs)

        @property
        def headers(self):
            self.header_reads += 1
            return Dataset.headers.fget(self)

        @headers.setter
        def headers(self, collection):
            Dataset.headers.fset(self, collection)

    def run(method):
        dataset = ObservedDataset(['Synthetic A'], ['Synthetic B'], headers=['name'])
        dataset.header_reads = 0
        result = method(dataset, rows=[0], cols=['name'])
        return list(result), dataset.header_reads

    assert run(Dataset.subset) == run(original_subset)


def test_subset_does_not_change_the_input():
    dataset = Dataset(['Synthetic A', 20], headers=['name', 'age'])
    state = copy(dataset._data), dataset.headers[:]
    dataset.subset(cols=['age', 'name', 'age'])
    assert (dataset._data, dataset.headers) == state
