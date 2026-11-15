from io import BytesIO

import pytest
from openpyxl import load_workbook

from tablib import Dataset
from tablib.exceptions import HeadersNeeded, InvalidDatasetType


def records(rows=(), headers=('id', 'value'), title=None):
    return Dataset(*rows, headers=headers, title=title)


@pytest.mark.parametrize('how, expected', [
    ('inner', [(2, 'a', 'x'), (2, 'a', 'y'), (2, 'c', 'x'), (2, 'c', 'y')]),
    ('left', [(2, 'a', 'x'), (2, 'a', 'y'), (1, 'b', None),
              (2, 'c', 'x'), (2, 'c', 'y')]),
    ('right', [(2, 'a', 'x'), (2, 'c', 'x'), (3, None, 'z'),
               (2, 'a', 'y'), (2, 'c', 'y')]),
    ('outer', [(2, 'a', 'x'), (2, 'a', 'y'), (1, 'b', None),
               (2, 'c', 'x'), (2, 'c', 'y'), (3, None, 'z')]),
])
def test_join_order_and_duplicates(how, expected):
    left = records([(2, 'a'), (1, 'b'), (2, 'c')])
    right = records([(2, 'x'), (3, 'z'), (2, 'y')])
    result = left.join(right, on='id', how=how)
    assert result.headers == ['id', 'value_left', 'value_right']
    assert list(result) == expected


def test_composite_differently_named_and_reordered_keys():
    left = records([('L', 1, 'a'), ('M', 1, 'b')], ('group', 'id', 'v'))
    right = records([('X', 'a', 1), ('Y', 'z', 2)], ('w', 'code', 'number'))
    result = left.join(right, left_on=['id', 'v'], right_on=['number', 'code'], how='outer')
    assert result.headers == ['group', 'id', 'v', 'w']
    assert list(result) == [('L', 1, 'a', 'X'), ('M', 1, 'b', None), (None, 2, 'z', 'Y')]


@pytest.mark.parametrize('how, expected', [
    ('inner', []), ('left', [(None, 'a', None), (None, 'b', None)]),
    ('right', [(None, None, 'c'), (None, None, 'd')]),
    ('outer', [(None, 'a', None), (None, 'b', None),
               (None, None, 'c'), (None, None, 'd')]),
])
def test_null_keys_never_match_or_violate_cardinality(how, expected):
    result = records([(None, 'a'), (None, 'b')]).join(
        records([(None, 'c'), (None, 'd')]), on='id', how=how, validate='one_to_one')
    assert list(result) == expected


def test_composite_null_and_python_key_equality():
    left = records([(1, None, 'null'), (True, 'x', 'yes')], ('a', 'b', 'l'))
    right = records([(1, None, 'null'), (1.0, 'x', 'match')], ('a', 'b', 'r'))
    result = left.join(right, on=('a', 'b'))
    assert list(result) == [(True, 'x', 'yes', 'match')]


@pytest.mark.parametrize('mode,left_rows,right_rows', [
    ('one_to_one', [(7, 'a'), (7, 'b')], []),
    ('one_to_one', [], [(8, 'c'), (8, 'd')]),
    ('one_to_many', [(7, 'a'), (7, 'b')], [(1, 'c')]),
    ('many_to_one', [(1, 'a')], [(8, 'c'), (8, 'd')]),
])
def test_cardinality_checks_unmatched_input_keys(mode, left_rows, right_rows):
    left, right = records(left_rows), records(right_rows)
    before = list(left), list(right)
    with pytest.raises(ValueError):
        left.join(right, on='id', validate=mode)
    assert (list(left), list(right)) == before


@pytest.mark.parametrize('mode,left_rows,right_rows', [
    ('one_to_many', [(1, 'a')], [(1, 'b'), (1, 'c')]),
    ('many_to_one', [(1, 'a'), (1, 'b')], [(1, 'c')]),
    ('many_to_many', [(1, 'a'), (1, 'b')], [(1, 'c'), (1, 'd')]),
])
def test_allowed_cardinality_modes(mode, left_rows, right_rows):
    result = records(left_rows).join(records(right_rows), on='id', validate=mode)
    assert len(result) == len(left_rows) * len(right_rows)


@pytest.mark.parametrize('left_rows,right_rows,how,expected', [
    ([], [], 'outer', []),
    ([], [(3, 'r')], 'outer', [(3, None, 'r')]),
    ([(2, 'l')], [], 'left', [(2, 'l', None)]),
    ([(2, 'l')], [], 'right', []),
    ([], [(3, 'r')], 'inner', []),
])
def test_empty_inputs_preserve_result_schema(left_rows, right_rows, how, expected):
    result = records(left_rows).join(records(right_rows), on='id', how=how)
    assert result.headers == ['id', 'value_left', 'value_right']
    assert list(result) == expected


@pytest.mark.parametrize('kwargs', [
    {}, {'on': []}, {'on': ('id', 'id')}, {'on': 'missing'},
    {'left_on': 'id'}, {'on': 'id', 'right_on': 'id'},
    {'left_on': ['id', 'value'], 'right_on': ['id']},
    {'on': 1}, {'on': {'id'}}, {'on': ['id', 1]},
    {'on': 'id', 'how': 'cross'}, {'on': 'id', 'validate': 'unique'},
    {'on': 'id', 'suffixes': ('x',)}, {'on': 'id', 'suffixes': (None, 'x')},
    {'on': 'id', 'suffixes': 'xy'}, {'on': 'id', 'suffixes': ('', '')},
])
def test_invalid_options_checked_even_when_empty(kwargs):
    with pytest.raises(ValueError):
        records().join(records(), **kwargs)


@pytest.mark.parametrize('headers', [('id', 'id'), ('id', ''), ('id', 42)])
def test_invalid_input_headers(headers):
    left, right = records(headers=headers), records()
    with pytest.raises(ValueError):
        left.join(right, on='id')
    with pytest.raises(ValueError):
        right.join(left, on='id')


def test_operand_and_missing_headers_errors():
    left = records([(1, 'a')])
    with pytest.raises(InvalidDatasetType):
        left.join([], on='id')
    with pytest.raises(HeadersNeeded):
        left.join(Dataset(), on='id')
    with pytest.raises(HeadersNeeded):
        Dataset().join(left, on='id')


@pytest.mark.parametrize('side', ['left', 'right'])
def test_unhashable_keys_rejected_even_without_matches(side):
    bad, empty = records([([], 'bad')]), records()
    left, right = (bad, empty) if side == 'left' else (empty, bad)
    with pytest.raises(TypeError):
        left.join(right, on='id')
    assert list(bad) == [([], 'bad')]


def test_suffix_collisions_and_key_payload_overlap():
    left = records([(1, 'l')], ('id', 'value'))
    right = records([(1, 'r')], ('key', 'id'))
    result = left.join(right, left_on='id', right_on='key', suffixes=('_a', '_b'))
    assert result.headers == ['id_a', 'value', 'id_b']
    assert list(result) == [(1, 'l', 'r')]
    collision = records(headers=('id', 'value', 'value_left'))
    with pytest.raises(ValueError):
        collision.join(records(), on='id')


def test_tags_title_and_rows_are_independent():
    cell = ['shared']
    left = records(headers=('id', 'l'), title='source')
    left.append((1, cell), tags=['left', 'common'])
    right = records(headers=('id', 'r'))
    right.append((1, 4), tags=['right', 'common'])
    right.append((2, 5), tags=['other'])
    result = left.join(right, on='id', how='outer')
    assert result.title == 'source'
    assert list(result.filter('common')) == [(1, cell, 4)]
    assert list(result.filter('right')) == [(1, cell, 4)]
    assert list(result.filter('other')) == [(2, None, 5)]
    assert result[0][1] is cell
    result[0] = (9, 'changed', 0)
    assert list(left) == [(1, cell)]
    assert list(right) == [(1, 4), (2, 5)]
    assert len(left.filter('left')) == 1
    assert len(right.filter('right')) == 1


def test_join_does_not_inherit_export_formatters():
    left = records([(1, 'plain')], title='left')
    left.add_formatter('value', str.upper)
    left.append_separator('source separator')
    result = left.join(records([(1, 'raw')]), on='id')
    assert result.dict == [{'id': 1, 'value_left': 'plain', 'value_right': 'raw'}]
    assert left.dict == [{'id': 1, 'value': 'PLAIN'}]
    sheet = load_workbook(BytesIO(result.xlsx)).active
    assert list(sheet.values) == [('id', 'value_left', 'value_right'), (1, 'plain', 'raw')]
    source_sheet = load_workbook(BytesIO(left.xlsx)).active
    assert source_sheet.max_row == 3


def test_self_join_and_key_only_schema():
    source = records([(1,), (1,), (2,)], ('id',))
    result = source.join(source, on='id')
    assert result.headers == ['id']
    assert list(result) == [(1,), (1,), (1,), (1,), (2,)]
    assert list(source) == [(1,), (1,), (2,)]
