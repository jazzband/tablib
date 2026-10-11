from io import BytesIO
from unittest.mock import patch

import pytest

from tablib import Dataset
from tablib._vendor.dbfpy import dbf
from tablib._vendor.dbfpy.fields import DbfCharacterFieldDef
from tablib._vendor.dbfpy.header import DbfHeader
from tablib.core import Row
from tablib.formats._dbf import DBFFormat


def dbf_bytes(names, rows):
    header = DbfHeader()
    header.setCurrentDate()
    header.addField(*[DbfCharacterFieldDef(name, 4) for name in names])
    header.recordCount = len(rows)
    stream = BytesIO()
    header.write(stream)
    for row in rows:
        stream.write(b' ' + b''.join(value.encode().ljust(4) for value in row))
    stream.write(b'\x1a')
    return stream.getvalue()


def original_import(dataset, stream):
    dataset.wipe()
    source = dbf.Dbf(stream)
    dataset.headers = source.fieldNames
    for index in range(source.recordCount):
        dataset.append([source[index][name] for name in source.fieldNames])


@pytest.mark.parametrize('names,rows', [
    (['a', 'b'], [['one', 'two'], ['x', 'y']]),
    (['a', 'a'], [['one', 'two']]),
    (['a', 'A'], [['one', 'two']]),
    (['a'], []),
    ([], []),
    ([], [[], []]),
])
def test_dbf_import_matches_original(names, rows):
    contents = dbf_bytes(names, rows)
    expected, actual = Dataset([99]), Dataset([99])
    before, after = BytesIO(contents), BytesIO(contents)
    original_import(expected, before)
    DBFFormat.import_set(actual, after)
    assert actual.headers == expected.headers
    assert list(actual) == list(expected)
    assert after.tell() == before.tell()


def test_dbf_import_reads_each_record_once():
    contents = dbf_bytes(['a', 'b', 'c'], [['1', '2', '3'], ['4', '5', '6']])
    original = dbf.Dbf.__getitem__
    calls = []

    def get_record(source, index):
        calls.append(index)
        return original(source, index)

    with patch.object(dbf.Dbf, '__getitem__', get_record):
        DBFFormat.import_set(Dataset(), BytesIO(contents))
    assert calls == [0, 1]


def test_dbf_import_custom_stream_keeps_read_count():
    class CountingStream(BytesIO):
        def __init__(self, contents):
            super().__init__(contents)
            self.reads = 0

        def read(self, *args):
            self.reads += 1
            return super().read(*args)

    contents = dbf_bytes(['a', 'b'], [['one', 'two']])
    before, after = CountingStream(contents), CountingStream(contents)
    expected, actual = Dataset(), Dataset()
    original_import(expected, before)
    DBFFormat.import_set(actual, after)
    assert list(actual) == list(expected)
    assert after.reads == before.reads


@pytest.mark.parametrize('contents', [
    b'', b'bad header', dbf_bytes(['a'], [['x']])[:-3],
    dbf_bytes(['a', 'b', 'c'], [['x', 'y', 'z'], ['1', '2', '3']])[:-4],
])
def test_dbf_import_malformed_stream_keeps_error(contents):
    def outcome(method):
        dataset = Dataset([99])
        stream = BytesIO(contents)
        try:
            method(dataset, stream)
        except Exception as error:
            return type(error), str(error), list(dataset), dataset.headers, stream.tell()
        return list(dataset), dataset.headers, stream.tell()

    assert outcome(DBFFormat.import_set) == outcome(original_import)


@pytest.mark.parametrize('headers', [['a', 'b'], ['a', 'a'], ['a', 'A']])
def test_dbf_export_matches_fallback(headers):
    dataset = Dataset(['one', 'two'], ['x', 'y'], headers=headers)
    expected = Dataset(headers=headers)

    class OriginalRow(Row):
        pass

    expected._data = [OriginalRow(row) for row in dataset]
    assert DBFFormat.export_set(dataset) == DBFFormat.export_set(expected)


@pytest.mark.parametrize('rows,columns', [(2, 5), (100, 10)])
def test_dbf_export_numeric_cells_match_fallback(rows, columns):
    class OriginalDataset(Dataset):
        pass

    values = [(1, 2.5, None, True, b'x'), (2, 3.5, '', False, b'y')]
    data = [values[index % 2] * (columns // 5) for index in range(rows)]
    headers = [f'f{index}' for index in range(columns)]
    actual = DBFFormat.export_set(Dataset(*data, headers=headers))
    expected = DBFFormat.export_set(OriginalDataset(*data, headers=headers))
    assert actual == expected


def test_dbf_export_custom_values_keep_name_lookups():
    class Value:
        def __str__(self):
            return 'x'

    dataset = Dataset([Value()], headers=['a'])
    calls = []
    original = dbf.Dbf.indexOfFieldName

    def lookup(source, name):
        calls.append(name)
        return original(source, name)

    with patch.object(dbf.Dbf, 'indexOfFieldName', lookup):
        DBFFormat.export_set(dataset)
    assert calls == ['a']


def test_dbf_export_truncated_unicode_header_keeps_error():
    class OriginalDataset(Dataset):
        pass

    # Each character occupies two UTF-8 bytes, exceeding DBF's name field.
    def outcome(dataset):
        try:
            return DBFFormat.export_set(dataset)
        except Exception as error:
            return type(error), str(error)

    assert outcome(Dataset(['x'], headers=['é' * 8])) == outcome(
        OriginalDataset(['x'], headers=['é' * 8])
    )


@pytest.mark.parametrize('rows,columns,fast', [
    (0, 2, False), (1, 1, False), (15, 1, False), (16, 1, True),
    (1, 2, True), (2, 2, True), (16, 0, False),
])
def test_dbf_import_dispatch_boundaries(rows, columns, fast):
    names = [f'f{index // 2}' for index in range(columns)]
    contents = dbf_bytes(names, [['x'] * columns for _ in range(rows)])
    expected, actual = Dataset(), Dataset()
    original_import(expected, BytesIO(contents))
    original = dbf.Dbf.indexOfFieldName
    calls = []

    def lookup(source, name):
        calls.append(name)
        return original(source, name)

    before, after = BytesIO(contents), BytesIO(contents)
    original_import(Dataset(), before)
    with patch.object(dbf.Dbf, 'indexOfFieldName', lookup):
        DBFFormat.import_set(actual, after)
    assert len(calls) == (0 if fast else rows * columns)
    assert list(actual) == list(expected)
    assert actual.headers == expected.headers
    assert after.tell() == before.tell()


@pytest.mark.parametrize('rows,columns,fast', [
    (9, 20, False), (10, 20, True), (100, 9, False),
    (99, 10, False), (100, 10, True), (100, 19, True),
])
def test_dbf_export_dispatch_boundaries(rows, columns, fast):
    class OriginalDataset(Dataset):
        pass

    headers = [f'f{index // 2}' for index in range(columns)]
    values = tuple(str(index) for index in range(columns))
    dataset = Dataset(*(values for _ in range(rows)), headers=headers)
    expected = DBFFormat.export_set(
        OriginalDataset(*(values for _ in range(rows)), headers=headers)
    )
    original = dbf.Dbf.indexOfFieldName
    calls = []

    def lookup(source, name):
        calls.append(name)
        return original(source, name)

    with patch.object(dbf.Dbf, 'indexOfFieldName', lookup):
        actual = DBFFormat.export_set(dataset)
    assert len(calls) == (0 if fast else rows * columns)
    assert actual == expected


def test_dbf_export_fast_sized_custom_value_keeps_lookups():
    class Value:
        def __str__(self):
            return 'x'

    headers = [f'f{index}' for index in range(20)]
    values = [Value()] + ['x'] * 19
    dataset = Dataset(*(values for _ in range(10)), headers=headers)
    original = dbf.Dbf.indexOfFieldName
    calls = []

    def lookup(source, name):
        calls.append(name)
        return original(source, name)

    with patch.object(dbf.Dbf, 'indexOfFieldName', lookup):
        DBFFormat.export_set(dataset)
    assert len(calls) == 200
