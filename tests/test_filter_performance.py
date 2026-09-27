from copy import copy
from random import Random
from unittest.mock import patch

import pytest

from tablib import Dataset
from tablib.core import Row


def original_filter(dataset, tag):
    result = copy(dataset)
    result._data = [row for row in result._data if row.has_tag(tag)]
    return result


@pytest.mark.parametrize('selection', [
    None, 'a', '', [], (), set(), frozenset(), ['a'],
    ['a', 'b'], ('a', 'b'), {'a', 'b'}, frozenset(('a', 'b')),
    ['a', 'a'], ['missing', 'other'], {'a': 1, 'b': 2}, b'ab', range(3),
])
def test_filter_matches_original(selection):
    dataset = Dataset(headers=['value'], title='Tagged')
    for value, tags in enumerate((['a'], ['b'], ['a', 'b'], [], ['missing'])):
        dataset.append([value], tags=tags)
    expected = original_filter(dataset, selection)
    actual = dataset.filter(selection)
    assert list(actual) == list(expected)
    assert actual.headers == expected.headers
    assert actual.title == expected.title
    assert actual._data == expected._data
    assert actual._data is not dataset._data
    assert all(row is source for row, source in zip(actual._data, expected._data))
    assert dataset.height == 5


@pytest.mark.parametrize('make_selection', [
    lambda: iter(['a', 'b']), lambda: (value for value in ('a', 'b')),
])
def test_filter_keeps_iterator_consumption(make_selection):
    dataset = Dataset(headers=['value'])
    dataset.append([1], tags=['a'])
    dataset.append([2], tags=['b'])
    selection = make_selection()
    assert list(dataset.filter(selection)) == [(1,)]
    assert list(selection) == []


@pytest.mark.parametrize('selection', [0, 1.5, [['a']], ['a', []]])
def test_filter_keeps_invalid_selection_errors(selection):
    dataset = Dataset([1])
    with pytest.raises(TypeError) as expected:
        original_filter(dataset, selection)
    with pytest.raises(TypeError) as actual:
        dataset.filter(selection)
    assert str(actual.value) == str(expected.value)


@pytest.mark.parametrize('selection', [None, 0, [['a']], ['a', 'b']])
def test_empty_filter_does_not_validate_selection(selection):
    assert Dataset().filter(selection).height == 0


@pytest.mark.parametrize('tags', [['a', []], [[]], ['a', {'x': 1}]])
def test_filter_still_validates_all_row_tags(tags):
    dataset = Dataset([1])
    dataset._data[0].tags = tags
    with pytest.raises(TypeError):
        dataset.filter(['a', 'b'])


def test_filter_preserves_custom_container_iteration():
    class ChangingSelection(list):
        def __init__(self):
            super().__init__()
            self.iterations = 0

        def __iter__(self):
            self.iterations += 1
            return iter(['a'] if self.iterations == 1 else ['b'])

    dataset = Dataset(headers=['value'])
    dataset.append([1], tags=['a'])
    dataset.append([2], tags=['b'])
    selection = ChangingSelection()
    assert list(dataset.filter(selection)) == [(1,), (2,)]
    assert selection.iterations == 2


def test_filter_preserves_row_override():
    class TaggedRow(Row):
        def has_tag(self, tag):
            return True

    dataset = Dataset()
    dataset._data = [TaggedRow([1])]
    dataset._data.append(Row([2], tags=['unselected']))
    selection = ['missing', 'other'] + [f'other{index}' for index in range(8)]
    assert list(dataset.filter(selection)) == [(1,)]


def test_filter_does_not_reorder_or_copy_selected_rows():
    dataset = Dataset(headers=['value'], title='Original')
    dataset.append([1], tags=['b'])
    dataset.append([2], tags=['a'])
    dataset.append([3], tags=['b'])
    dataset.add_formatter('value', str)
    result = dataset.filter(['a', 'b'] + [f'other{index}' for index in range(8)])
    assert list(result) == [(1,), (2,), (3,)]
    assert result._formatters is dataset._formatters
    assert result._data[0] is dataset._data[0]


def test_filter_custom_hash_calls_match_original():
    class Tag:
        def __init__(self):
            self.hash_calls = 0

        def __hash__(self):
            self.hash_calls += 1
            return 1

    def run(method):
        tag = Tag()
        dataset = Dataset([1], [2])
        for row in dataset._data:
            row.tags = [tag]
        result = method(dataset, [tag] + [f'other{index}' for index in range(9)])
        return list(result), tag.hash_calls

    assert run(Dataset.filter) == run(original_filter)


def test_filter_randomized_equivalence():
    random = Random(686)
    containers = (list, tuple, set, frozenset)
    for _ in range(500):
        dataset = Dataset(headers=['value'])
        for value in range(random.randrange(20)):
            dataset.append([value], tags=[
                random.choice(('a', 'b', 'c', '雪', '')) for _ in range(random.randrange(8))
            ])
        selection = random.choice(containers)(
            random.choice(('a', 'b', 'missing', '雪', '')) for _ in range(random.randrange(40))
        )
        expected = original_filter(dataset, selection)
        actual = dataset.filter(selection)
        assert actual._data == expected._data
        assert actual.headers == expected.headers


def test_filter_large_selection_keeps_order_and_duplicates():
    dataset = Dataset(headers=['value'])
    for value, tags in enumerate((['b'], ['a'], ['missing'], ['b'])):
        dataset.append([value], tags=tags)
    selection = ['a', 'b', 'a'] + [f'other{index}' for index in range(20)]
    assert list(dataset.filter(selection)) == [(0,), (1,), (3,)]


@pytest.mark.parametrize('rows,queries,row_tags,fast', [
    (15, 20, 3, False), (16, 19, 3, False), (16, 20, 3, True),
    (16, 20, 10, True), (16, 20, 11, False), (2, 100, 3, False),
])
@pytest.mark.parametrize('container', [list, tuple, set, frozenset])
def test_filter_dispatch_boundaries(rows, queries, row_tags, fast, container):
    dataset = Dataset(headers=['value'], title='Boundary')
    for value in range(rows):
        tags = [f'tag{index}' for index in range(row_tags)]
        if value % 2:
            tags[-1] = 'wanted'
        dataset.append([value], tags=tags)
    selection = container(['wanted'] + [f'query{index}' for index in range(queries - 1)])
    expected = original_filter(dataset, selection)
    original = Row.has_tag
    calls = []

    def has_tag(row, tag):
        calls.append(row)
        return original(row, tag)

    with patch.object(Row, 'has_tag', has_tag):
        actual = dataset.filter(selection)
    assert len(calls) == (0 if fast else rows)
    assert actual._data == expected._data
    assert actual.headers == expected.headers
    assert actual.title == expected.title


def test_filter_fast_sized_unhashable_tags_keep_original_error():
    dataset = Dataset(*([index] for index in range(16)))
    dataset._data[-1].tags = ['wanted', []]
    selection = ['wanted'] + [f'query{index}' for index in range(19)]
    with pytest.raises(TypeError) as expected:
        original_filter(dataset, selection)
    with pytest.raises(TypeError) as actual:
        dataset.filter(selection)
    assert str(actual.value) == str(expected.value)


def test_filter_fast_sized_row_override_is_used():
    class TaggedRow(Row):
        def has_tag(self, tag):
            return True

    dataset = Dataset(*([index] for index in range(16)))
    dataset._data[-1] = TaggedRow([15])
    selection = [f'query{index}' for index in range(20)]
    assert dataset.filter(selection)._data == original_filter(dataset, selection)._data
    assert list(dataset.filter(selection)) == [(15,)]


def test_filter_fast_sized_custom_hash_calls_match_original():
    class Tag:
        def __init__(self):
            self.hash_calls = 0

        def __hash__(self):
            self.hash_calls += 1
            return 1

    def run(method):
        tag = Tag()
        dataset = Dataset(*([index] for index in range(16)))
        for row in dataset._data:
            row.tags = [tag]
        result = method(dataset, [tag] + [f'other{index}' for index in range(19)])
        return list(result), tag.hash_calls

    assert run(Dataset.filter) == run(original_filter)
