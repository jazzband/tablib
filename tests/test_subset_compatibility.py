from copy import copy
from unittest.mock import patch

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
@pytest.mark.parametrize('height', [2, 16])
def test_subset_selector_changing_headers_keeps_key_error(rows, height):
    dataset = Dataset(*(['Synthetic A', 20] for _ in range(height)), headers=['name', 'age'])

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
@pytest.mark.parametrize('height', [2, 16])
def test_subset_preserves_stateful_comparisons_and_their_errors(rows, at, raises, height):
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

        dataset = Dataset(*(['Synthetic A'] for _ in range(height)), headers=['name'])
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


@pytest.mark.parametrize('height', [2, 16, 64])
@pytest.mark.parametrize('action', ['wipe', 'remove_and_rename', 'rows_with_no_columns'])
def test_subset_selector_emptying_the_source_matches_original(height, action):
    def run(method):
        dataset = Dataset(*([index] for index in range(height)), headers=['value'])

        def columns():
            yield 'value'
            if action == 'wipe':
                dataset.wipe()
            else:
                del dataset[:]
                dataset.headers = ['renamed']

        def rows():
            del dataset[:]
            yield 0

        if action == 'rows_with_no_columns':
            result = method(dataset, rows=rows(), cols=[])
        else:
            result = method(dataset, cols=columns())
        return list(result), result.headers

    assert run(Dataset.subset) == run(original_subset)


@pytest.mark.parametrize('height', [2, 16, 64])
@pytest.mark.parametrize('rows', [[], [0], [1]])
def test_subset_keeps_errors_from_unselected_short_rows(height, rows):
    def run(method):
        dataset = Dataset(*([index, index + 100] for index in range(height - 1)),
                          [999], headers=['a', 'b'])
        with pytest.raises(IndexError) as error:
            method(dataset, rows=rows, cols=['b'])
        return error.value.args

    assert run(Dataset.subset) == run(original_subset)


@pytest.mark.parametrize('height', [2, 16, 64])
@pytest.mark.parametrize('rows', [[], [0]])
def test_subset_keeps_index_errors_after_public_header_mutation(height, rows):
    dataset = Dataset(*([index, index + 100] for index in range(height)), headers=['a', 'b'])
    dataset.headers.append('extra')
    with pytest.raises(IndexError) as expected:
        original_subset(dataset, rows=rows, cols=['extra'])
    with pytest.raises(IndexError) as actual:
        dataset.subset(rows=rows, cols=['extra'])
    assert actual.value.args == expected.value.args


@pytest.mark.parametrize('height', [2, 16, 64])
@pytest.mark.parametrize('customize', ['row', 'cells', 'container', 'method'])
def test_subset_keeps_custom_row_reads_and_header_changes(height, customize):
    def run(method):
        dataset = Dataset(*([index, index + 100] for index in range(height)),
                          headers=['a', 'b'])
        events = []
        original_getitem = Row.__getitem__

        def read(row, index):
            value = original_getitem(row, index)
            events.append(index)
            dataset.headers[:] = ['b', 'a']
            return value

        class CustomRow(Row):
            def __getitem__(self, index):
                return read(self, index)

        class Cells(list):
            def __getitem__(self, index):
                value = super().__getitem__(index)
                events.append(index)
                dataset.headers[:] = ['b', 'a']
                return value

        class Rows(list):
            def __iter__(self):
                events.append('iter')
                dataset.headers[:] = ['b', 'a']
                return super().__iter__()

        if customize == 'row':
            dataset._data[0] = CustomRow([0, 100])
        elif customize == 'cells':
            dataset._data[0]._row = Cells([0, 100])
        elif customize == 'container':
            dataset._data = Rows(dataset._data)
        if customize == 'method':
            with patch.object(Row, '__getitem__', read):
                result = method(dataset, cols=['a'])
        else:
            result = method(dataset, cols=['a'])
        return list(result), dataset.headers, events

    assert run(Dataset.subset) == run(original_subset)


def test_subset_keeps_selector_comparison_side_effects():
    def run(method):
        dataset = Dataset(*([index, index + 100] for index in range(16)),
                          headers=['a', 'b'])
        calls = []

        class Selector:
            __hash__ = None

            def __eq__(self, other):
                calls.append(other)
                if len(calls) > 1:
                    dataset.headers.reverse()
                return True

        result = method(dataset, rows=[Selector()], cols=['a'])
        return list(result), dataset.headers, calls

    assert run(Dataset.subset) == run(original_subset)


@pytest.mark.parametrize('custom_first', [True, False])
def test_subset_source_header_comparison_calls_match_original(custom_first):
    def run(method):
        calls = []

        class Header(str):
            def __eq__(self, other):
                calls.append(other)
                return super().__eq__(other)

        headers = [Header('custom'), 'wanted'] if custom_first else ['wanted', Header('custom')]
        dataset = Dataset(*([index, index + 100] for index in range(16)), headers=headers)
        result = method(dataset, rows=[0], cols=['wanted'])
        return list(result), calls

    assert run(Dataset.subset) == run(original_subset)


def test_subset_uses_first_header_occurrences_on_the_cached_path():
    dataset = Dataset(*([index, index + 100, index + 200] for index in range(16)),
                      headers=['a', 'a', 'b'])
    expected = original_subset(dataset, rows=[15, 0, 15], cols=['b', 'a', 'b'])
    result = dataset.subset(rows=[15, 0, 15], cols=['b', 'a', 'b'])
    assert result.headers == expected.headers
    assert list(result) == list(expected)


def test_subset_header_removed_by_selector_keeps_key_error_on_cached_path():
    dataset = Dataset(*([index, index + 100] for index in range(16)), headers=['a', 'b'])

    def columns():
        yield 'a'
        dataset.headers = ['renamed', 'b']

    with pytest.raises(KeyError) as error:
        dataset.subset(cols=columns())
    assert error.value.args == ()
    assert error.value.__context__ is None
