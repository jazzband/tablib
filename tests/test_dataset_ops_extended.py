"""Extended Dataset operation coverage for tablib.

All of these operations return a new Dataset (except the in-place
``insert_col``/``append_col`` family and ``add_formatter``), which
the tests assert explicitly for sort, transpose, stack, stack_cols,
subset and filter.
"""

import pytest

from tablib import Dataset
from tablib.exceptions import HeadersNeeded, InvalidDatasetIndex, InvalidDimensions


def mk(rows=((1, 2), (3, 4)), headers=("a", "b")):
    d = Dataset(headers=list(headers))
    for row in rows:
        d.append(row)
    return d


# ---------------------------------------------------------------- sort

def test_sort_by_header_ascending_and_descending():
    d = mk(((2, 1), (1, 2)))
    assert list(d.sort("a")) == [(1, 2), (2, 1)]
    assert list(d.sort("a", reverse=True)) == [(2, 1), (1, 2)]
    assert list(d) == [(2, 1), (1, 2)]  # original unchanged


def test_sort_by_index_uses_header_name_when_headers_exist():
    # With headers, sort(1) sorts by the second header ("b"), not by
    # raw position: (2, 1) has b=1, so it comes first.
    d = mk(((2, 1), (1, 2)))
    assert list(d.sort(1)) == [(2, 1), (1, 2)]


def test_sort_without_headers_by_index():
    d = Dataset()
    d.append((2,))
    d.append((1,))
    assert list(d.sort(0)) == [(1,), (2,)]


def test_sort_by_header_without_headers_raises():
    d = Dataset()
    d.append((1,))
    with pytest.raises(HeadersNeeded):
        d.sort("a")


# ---------------------------------------------------------------- transpose / stack

def test_transpose_with_headers():
    transposed = mk().transpose()
    assert transposed.headers == ["a", 1, 3]
    assert list(transposed) == [("b", 2, 4)]


def test_transpose_without_headers():
    d = Dataset()
    d.append((1, 2))
    d.append((3, 4))
    assert list(d.transpose()) == [(1, 3), (2, 4)]


def test_transpose_empty_is_none():
    assert Dataset().transpose() is None


def test_stack_combines_rows_and_keeps_original():
    a = mk(((1,),), ("a",))
    b = mk(((2,),), ("a",))
    stacked = a.stack(b)
    assert list(stacked) == [(1,), (2,)]
    assert list(a) == [(1,)]


def test_stack_width_mismatch_and_type_errors():
    with pytest.raises(InvalidDimensions):
        mk().stack(mk(((1,),), ("a",)))
    with pytest.raises(TypeError):
        mk().stack([(1,)])


def test_stack_cols_with_and_without_headers():
    a = mk(((1,),), ("a",))
    b = mk(((2,),), ("b",))
    combined = a.stack_cols(b)
    assert combined.headers == ["a", "b"]
    assert list(combined) == [(1, 2)]
    no_headers = Dataset((1,), (2,)).stack_cols(Dataset((3,), (4,)))
    assert no_headers.headers is None
    assert list(no_headers) == [(1, 3), (2, 4)]


def test_stack_cols_header_mismatch_raises():
    with pytest.raises(HeadersNeeded):
        mk(((1,),), ("a",)).stack_cols(Dataset((2,)))


# ---------------------------------------------------------------- subset / filter

def test_subset_rows_and_cols():
    d = Dataset(headers=["a"])
    d.append((1,))
    d.append((2,))
    d.append((3,))
    assert list(d.subset(rows=(0, 2))) == [(1,), (3,)]
    sub = mk().subset(cols=("b",))
    assert sub.headers == ["b"]
    assert list(sub) == [(2,), (4,)]


def test_subset_filters_impossible_entries_silently():
    sub = mk().subset(rows=(0, 99), cols=("a", "zz"))
    assert sub.headers == ["a"]
    assert list(sub) == [(1,)]


def test_subset_empty_is_none():
    assert Dataset().subset() is None


def test_filter_by_tag_returns_new_dataset():
    d = mk()
    d.append((5, 6), tags=["x"])
    filtered = d.filter("x")
    assert list(filtered) == [(5, 6)]
    assert list(d) == [(1, 2), (3, 4), (5, 6)]


# ---------------------------------------------------------------- columns / formatters

def test_insert_col_and_append_col():
    d = mk()
    d.insert_col(1, [9, 8], header="c")
    assert d.headers == ["a", "c", "b"]
    assert list(d) == [(1, 9, 2), (3, 8, 4)]
    d = mk()
    d.append_col([9, 8], header="c")
    assert d.headers == ["a", "b", "c"]
    assert list(d) == [(1, 2, 9), (3, 4, 8)]


def test_insert_col_requires_header_when_headers_exist():
    with pytest.raises(HeadersNeeded):
        mk().insert_col(1, [9, 8])


def test_insert_col_callable_computes_per_row():
    d = mk()
    d.insert_col(1, lambda row: row[0] * 10, header="c")
    assert list(d) == [(1, 10, 2), (3, 30, 4)]


def test_get_col_by_index():
    assert mk().get_col(1) == [2, 4]


def test_add_formatter_by_name_index_and_all():
    d = mk()
    assert d.add_formatter("a", lambda v: v * 10) is True
    # Formatters apply to the dict view (and exports), not to raw
    # column access: d["a"] still returns the stored values.
    assert d["a"] == [1, 3]
    assert d.dict == [{"a": 10, "b": 2}, {"a": 30, "b": 4}]
    d = mk()
    d.add_formatter(None, lambda v: v + 1)
    assert d.dict == [{"a": 2, "b": 3}, {"a": 4, "b": 5}]


def test_add_formatter_bad_column_errors():
    with pytest.raises(InvalidDatasetIndex):
        mk().add_formatter(99, lambda v: v)
    with pytest.raises(KeyError):
        mk().add_formatter("zz", lambda v: v)


def test_separators_recorded_but_not_in_row_iteration():
    d = mk()
    d.append_separator()
    assert d._separators == [(3, "-")]
    assert list(d) == [(1, 2), (3, 4)]
