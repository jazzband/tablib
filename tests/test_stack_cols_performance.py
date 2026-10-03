from random import Random
from unittest.mock import patch

import pytest

from tablib import Dataset
from tablib.core import Row
from tablib.exceptions import HeadersNeeded, InvalidDimensions


def original_stack_cols(left, right):
    if not isinstance(right, Dataset):
        raise TypeError("'other' must be a Dataset instance")
    if left.headers or right.headers:
        if not left.headers or not right.headers:
            raise HeadersNeeded
    if left.height != right.height:
        raise InvalidDimensions
    try:
        headers = left.headers + right.headers
    except TypeError:
        headers = None
    result = Dataset()
    if left.headers:
        for header in left.headers:
            result.append_col(col=left[header])
        for header in right.headers:
            result.append_col(col=right[header])
    else:
        for index in range(left.width):
            result.append_col(col=left.get_col(index))
        for index in range(right.width):
            result.append_col(col=right.get_col(index))
    result.headers = headers
    return result


@pytest.mark.parametrize('rows', [0, 1, 2, 20])
@pytest.mark.parametrize('widths', [(0, 0), (0, 2), (2, 0), (1, 1), (2, 3), (20, 8)])
@pytest.mark.parametrize('headers', [False, True])
def test_stack_cols_matches_original(rows, widths, headers):
    datasets = []
    for offset, width in zip((0, 100), widths):
        names = [f'col{index}' for index in range(width)] if headers else None
        dataset = Dataset(headers=names, title='Not retained')
        for row in range(rows):
            dataset.append([offset + row * width + col for col in range(width)], tags=['tag'])
        datasets.append(dataset)
    if headers and 0 in widths and widths != (0, 0):
        with pytest.raises(HeadersNeeded):
            original_stack_cols(*datasets)
        with pytest.raises(HeadersNeeded):
            datasets[0].stack_cols(datasets[1])
        return
    expected = original_stack_cols(*datasets)
    actual = datasets[0].stack_cols(datasets[1])
    assert list(actual) == list(expected)
    assert actual.headers == expected.headers
    assert actual.title == expected.title
    assert [row.tags for row in actual._data] == [row.tags for row in expected._data]


def test_stack_cols_duplicate_headers_use_first_column():
    left = Dataset([1, 2, 3], headers=['x', 'x', 'y'])
    right = Dataset([4, 5], headers=['x', 'x'])
    result = left.stack_cols(right)
    assert list(result) == [(1, 1, 3, 4, 4)]
    assert result.headers == ['x', 'x', 'y', 'x', 'x']


def test_stack_cols_keeps_cell_references_but_copies_rows():
    cell = []
    left = Dataset([cell], headers=['x'])
    right = Dataset([None], headers=['y'])
    result = left.stack_cols(right)
    assert result[0][0] is cell
    assert result._data[0] is not left._data[0]
    result._data[0][1] = 2
    assert right[0][0] is None


@pytest.mark.parametrize('left,right,error', [
    (Dataset([1], headers=['x']), Dataset([2]), HeadersNeeded),
    (Dataset([1]), Dataset([2], headers=['y']), HeadersNeeded),
    (Dataset([1]), Dataset([2], [3]), InvalidDimensions),
    (Dataset([1]), None, TypeError),
])
def test_stack_cols_keeps_errors(left, right, error):
    with pytest.raises(error) as expected:
        original_stack_cols(left, right)
    with pytest.raises(error) as actual:
        left.stack_cols(right)
    assert str(actual.value) == str(expected.value)


@pytest.mark.parametrize('headers', [[0, 1], ['x', 0], [None, 'x'], [[], 'x']])
def test_stack_cols_unusual_headers_keep_original_behavior(headers):
    left = Dataset([1, 2], [3, 4], headers=headers)
    right = Dataset([5, 6], [7, 8], headers=headers)
    try:
        expected = original_stack_cols(left, right)
    except Exception as expected:
        with pytest.raises(type(expected)) as actual:
            left.stack_cols(right)
        assert str(actual.value) == str(expected)
    else:
        assert list(left.stack_cols(right)) == list(expected)


def test_stack_cols_dataset_override_is_used():
    class CustomDataset(Dataset):
        def __getitem__(self, key):
            if isinstance(key, str):
                return [99] * self.height
            return super().__getitem__(key)

    left = CustomDataset([1], headers=['x'])
    right = Dataset([2], headers=['y'])
    assert list(left.stack_cols(right)) == [(99, 2)]


def test_stack_cols_row_override_is_used():
    class CustomRow(Row):
        def __getitem__(self, key):
            return 99

    left = Dataset([1], headers=['x'])
    left._data[0] = CustomRow([1])
    right = Dataset([2], headers=['y'])
    assert list(left.stack_cols(right)) == [(99, 2)]


def test_stack_cols_mutated_ragged_rows_keep_error():
    left = Dataset([1, 2], [3, 4], headers=['x', 'y'])
    left._data[1]._row.pop()
    right = Dataset([5], [6], headers=['z'])
    with pytest.raises(IndexError):
        left.stack_cols(right)


def test_stack_cols_randomized_equivalence():
    random = Random(687)
    for _ in range(500):
        rows = random.randrange(10)
        headed = random.choice((True, False))
        datasets = []
        for _ in range(2):
            width = random.randrange(1 if headed else 0, 10)
            headers = (
                [random.choice(('a', 'b', '雪', '')) for _ in range(width)] if headed else None
            )
            dataset = Dataset(headers=headers)
            for _ in range(rows):
                dataset.append([random.choice((None, 1, 'x', False)) for _ in range(width)])
            datasets.append(dataset)
        expected = original_stack_cols(*datasets)
        actual = datasets[0].stack_cols(datasets[1])
        assert actual.headers == expected.headers
        assert list(actual) == list(expected)


@pytest.mark.parametrize('columns', [15, 16, 17])
@pytest.mark.parametrize('rows', [0, 1, 16])
@pytest.mark.parametrize('headerless', [False, True])
def test_stack_cols_dispatch_boundaries(columns, rows, headerless):
    datasets = []
    for width in (columns // 2, columns - columns // 2):
        headers = None if headerless else [f'col{index // 2}' for index in range(width)]
        datasets.append(Dataset(*(tuple(range(width)) for _ in range(rows)), headers=headers))
    expected = original_stack_cols(*datasets)
    original = Dataset.append_col
    calls = []

    def append_col(dataset, *args, **kwargs):
        calls.append(dataset)
        return original(dataset, *args, **kwargs)

    with patch.object(Dataset, 'append_col', append_col):
        actual = datasets[0].stack_cols(datasets[1])
    actual_width = 0 if headerless and rows == 0 else columns
    assert len(calls) == (actual_width if columns < 16 else 0)
    assert actual.headers == expected.headers
    assert list(actual) == list(expected)


def test_stack_cols_wide_custom_row_keeps_access_override():
    class CustomRow(Row):
        def __getitem__(self, key):
            return 99

    left = Dataset(tuple(range(8)), headers=[f'left{index}' for index in range(8)])
    left._data[0] = CustomRow(range(8))
    right = Dataset(tuple(range(8)), headers=[f'right{index}' for index in range(8)])
    expected = original_stack_cols(left, right)
    assert list(left.stack_cols(right)) == list(expected)


def test_stack_cols_wide_ragged_rows_keep_original_error():
    left = Dataset(
        tuple(range(8)), tuple(range(8)), headers=[f'left{index}' for index in range(8)]
    )
    right = Dataset(
        tuple(range(8)), tuple(range(8)), headers=[f'right{index}' for index in range(8)]
    )
    left._data[-1]._row.pop()
    with pytest.raises(IndexError) as expected:
        original_stack_cols(left, right)
    with pytest.raises(IndexError) as actual:
        left.stack_cols(right)
    assert str(actual.value) == str(expected.value)
