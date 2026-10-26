"""Extended Dataset / Row core coverage for tablib.

Probed behaviours pinned here:

* ``sort``/``transpose``/``stack``/``stack_cols``/``subset``/``filter``
  all return a *new* Dataset; the original is unchanged.
* ``Dataset.pop()`` takes no index argument (it pops the last row);
  ``lpop``/``rpop`` pop the first/last row respectively.
* ``Dataset.__setitem__`` only accepts row positions: a string key
  raises ``TypeError`` (it indexes the internal row list).
* ``subset`` silently drops impossible rows/columns instead of
  raising, and its ``cols`` are header *names*, not indices.
* ``transpose`` on an empty Dataset (and ``subset`` on one) returns
  ``None``, not an empty Dataset.
"""

import pytest

from tablib import Dataset
from tablib.core import Row
from tablib.exceptions import (
    HeadersNeeded,
    InvalidDatasetIndex,
    InvalidDimensions,
)


def mk(rows=((1, 2), (3, 4)), headers=("a", "b")):
    d = Dataset(headers=list(headers))
    for row in rows:
        d.append(row)
    return d


# ---------------------------------------------------------------- Row

def test_row_basic_operations():
    row = Row((1, 2))
    row.append(3)
    row.insert(0, 0)
    row.lpush(-1)
    row.rpush(9)
    assert row.list == [-1, 0, 1, 2, 3, 9]
    assert row.tuple == (-1, 0, 1, 2, 3, 9)
    assert len(row) == 6
    assert 3 in row
    assert 99 not in row


def test_row_get_set_del_and_slice():
    row = Row((1, 2, 3))
    assert row[0] == 1
    assert row[0:2] == [1, 2]
    row[0] = 99
    del row[1]
    assert row.list == [99, 3]


def test_row_copy_is_independent():
    row = Row((1, 2))
    copied = row.copy()
    assert copied.list == [1, 2]
    assert copied is not row
    copied.append(3)
    assert row.list == [1, 2]


def test_row_tags():
    row = Row((1,), tags=["t"])
    assert row.has_tag("t") is True
    assert row.has_tag("other") is False


# ---------------------------------------------------------------- Dataset basics

def test_len_height_width():
    d = mk()
    assert len(d) == 2
    assert d.height == 2
    assert d.width == 2
    assert Dataset(headers=["a", "b"]).width == 2
    assert Dataset().width == 0
    assert Dataset().height == 0


def test_getitem_row_col_slice():
    d = mk()
    assert d[0] == (1, 2)
    assert d["a"] == [1, 3]
    assert d[0:1] == [(1, 2)]


def test_getitem_unknown_header_and_no_headers():
    d = mk()
    with pytest.raises(KeyError):
        d["zz"]
    with pytest.raises(HeadersNeeded):
        Dataset((1,), (2,))["a"]


def test_setitem_row_and_delitem_row_and_col():
    d = mk()
    d[0] = (9, 9)
    assert list(d) == [(9, 9), (3, 4)]
    del d[0]
    assert list(d) == [(3, 4)]
    d = mk()
    del d["a"]
    assert d.headers == ["b"]
    assert list(d) == [(2,), (4,)]


def test_setitem_string_key_raises_type_error():
    d = mk()
    with pytest.raises(TypeError):
        d["a"] = [9, 8]


def test_append_insert_and_dimension_errors():
    d = mk()
    d.insert(0, (0, 0))
    assert d[0] == (0, 0)
    with pytest.raises(InvalidDimensions):
        d.append((1,))
    with pytest.raises(InvalidDimensions):
        d.headers = ["x"]


def test_lpush_rpush_lpop_rpop_pop():
    d = mk()
    d.lpush((-1, -1))
    d.rpush((5, 6))
    assert d[0] == (-1, -1)
    assert d[-1] == (5, 6)
    assert d.lpop() == (-1, -1)
    assert d.rpop() == (5, 6)
    assert d.pop() == (3, 4)
    assert list(d) == [(1, 2)]


def test_pop_takes_no_index():
    d = mk()
    with pytest.raises(TypeError):
        d.pop(0)


def test_get_and_get_out_of_range():
    d = mk()
    assert d.get(0) == (1, 2)
    with pytest.raises(IndexError):
        d.get(99)


def test_dict_property_and_setter():
    d = mk()
    assert d.dict == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    d.dict = [{"a": 9, "b": 8}]
    assert list(d) == [(9, 8)]


def test_headers_setter():
    d = mk()
    d.headers = ["x", "y"]
    assert d.headers == ["x", "y"]
    assert d["x"] == [1, 3]


def test_title_and_repr():
    assert Dataset(title="MyTitle").title == "MyTitle"
    assert repr(Dataset(title="MyTitle")) == "<mytitle dataset>"
    assert repr(Dataset()) == "<dataset object>"


def test_str_representation():
    assert str(mk()) == "a|b\n-|-\n1|2\n3|4"


def test_init_with_rows_and_headers():
    d = Dataset((1, 2), (3, 4), headers=["a", "b"])
    assert list(d) == [(1, 2), (3, 4)]


def test_wipe_clears_data_and_headers():
    d = mk()
    d.wipe()
    assert len(d) == 0
    assert d.headers is None


def test_remove_duplicates_keeps_order():
    d = Dataset(headers=["a"])
    d.append((1,))
    d.append((1,))
    d.append((2,))
    d.remove_duplicates()
    assert list(d) == [(1,), (2,)]
