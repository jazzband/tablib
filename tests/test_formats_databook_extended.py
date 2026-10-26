"""Extended format export/load and Databook coverage for tablib.

Only formats with no heavy optional dependencies are covered here
(csv/tsv/json/yaml/html/jira/rst/latex); xls/xlsx/ods/df/sql need
extra packages and are out of scope for this suite. Probed
behaviours pinned here:

* csv/tsv exports use ``\\r\\n`` line endings.
* Loading csv treats the first line as headers, and all loaded
  values are strings.
* Databook ``sheets`` is a method, not a property.
* Exporting/loading an unknown format raises ``UnsupportedFormat``.
"""

import pytest

from tablib import Databook, Dataset
from tablib.exceptions import InvalidDatasetType, UnsupportedFormat


def mk():
    d = Dataset(headers=["a", "b"])
    d.append((1, 2))
    return d


# ---------------------------------------------------------------- exports

def test_export_csv_and_tsv_line_endings():
    assert mk().export("csv") == "a,b\r\n1,2\r\n"
    assert mk().export("tsv") == "a\tb\r\n1\t2\r\n"


def test_export_json():
    assert mk().export("json") == '[{"a": 1, "b": 2}]'


def test_export_yaml():
    assert mk().export("yaml") == "- {a: 1, b: 2}\n"


def test_export_html():
    assert mk().export("html") == (
        "<table><thead><tr><th>a</th><th>b</th></tr></thead>"
        "<tbody><tr><td>1</td><td>2</td></tr></tbody></table>"
    )


def test_export_jira():
    assert mk().export("jira") == "||a||b||\n|1|2|"


def test_export_rst():
    assert mk().export("rst") == "=  =\na  b\n=  =\n1  2\n=  ="


def test_export_latex_contains_table_structure():
    latex = mk().export("latex")
    assert "\\begin{table}" in latex
    assert "a & b" in latex
    assert "1 & 2" in latex


def test_export_unknown_format_raises():
    with pytest.raises(UnsupportedFormat):
        mk().export("nope")


def test_export_csv_roundtrip_via_load():
    d = Dataset()
    d.load(mk().export("csv"), format="csv")
    assert d.headers == ["a", "b"]
    # csv values load back as strings.
    assert list(d) == [("1", "2")]


# ---------------------------------------------------------------- loads

def test_load_csv_first_line_is_headers():
    d = Dataset()
    d.load("a,b\n1,2\n", format="csv")
    assert d.headers == ["a", "b"]
    assert list(d) == [("1", "2")]


def test_load_csv_without_header_line_uses_first_row_as_headers():
    d = Dataset()
    d.load("1,2\n3,4\n", format="csv")
    assert d.headers == ["1", "2"]
    assert list(d) == [("3", "4")]


def test_load_tsv():
    d = Dataset()
    d.load("a\tb\n1\t2\n", format="tsv")
    assert d.headers == ["a", "b"]
    assert list(d) == [("1", "2")]


def test_load_json():
    d = Dataset()
    d.load('[{"a": 1}]', format="json")
    assert d.headers == ["a"]
    assert list(d) == [(1,)]


def test_load_yaml():
    d = Dataset()
    d.load("- {a: 1, b: 2}\n", format="yaml")
    assert d.headers == ["a", "b"]
    assert list(d) == [(1, 2)]


def test_load_unknown_format_raises():
    with pytest.raises(UnsupportedFormat):
        Dataset().load("x", format="nope")


def test_load_returns_self():
    d = Dataset()
    assert d.load("a,b\n1,2\n", format="csv") is d


# ---------------------------------------------------------------- Databook

def test_databook_add_sheet_size_and_wipe():
    book = Databook()
    book.add_sheet(mk())
    assert book.size == 1
    assert len(book.sheets()) == 1
    assert book.sheets()[0] is not None
    book.wipe()
    assert book.size == 0


def test_databook_init_with_sheets():
    book = Databook((mk(), mk()))
    assert book.size == 2


def test_databook_rejects_non_dataset_sheet():
    with pytest.raises(InvalidDatasetType):
        Databook().add_sheet("x")


def test_databook_repr_without_title():
    assert repr(Databook()) == "<databook object>"


def test_databook_export_json():
    book = Databook()
    book.add_sheet(mk())
    assert book.export("json") == '[{"title": null, "data": [{"a": 1, "b": 2}]}]'


def test_databook_export_json_with_titled_sheet():
    d = Dataset(headers=["a"], title="Sheet1")
    d.append((1,))
    book = Databook((d,))
    assert book.export("json") == '[{"title": "Sheet1", "data": [{"a": 1}]}]'
