#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for Tablib."""

import json
import unittest
import sys
import os
import tablib
from tablib.compat import markup, unicode, is_py3





class TablibTestCase(unittest.TestCase):
    """Tablib test cases."""

    def setUp(self):
        """Create simple data set with headers."""

        global data, book

        data = tablib.Dataset()
        book = tablib.Databook()

        self.headers = ('first_name', 'last_name', 'gpa')
        self.john = ('John', 'Adams', 90)
        self.george = ('George', 'Washington', 67)
        self.tom = ('Thomas', 'Jefferson', 50)

        self.founders = tablib.Dataset(headers=self.headers, title='Founders')
        self.founders.append(self.john)
        self.founders.append(self.george)
        self.founders.append(self.tom)


    def tearDown(self):
        """Teardown."""
        pass


    def test_empty_append(self):
        """Verify append() correctly adds tuple with no headers."""
        new_row = (1, 2, 3)
        data.append(new_row)

        # Verify width/data
        self.assertTrue(data.width == len(new_row))
        self.assertTrue(data[0] == new_row)


    def test_empty_append_with_headers(self):
        """Verify append() correctly detects mismatch of number of
        headers and data.
        """
        data.headers = ['first', 'second']
        new_row = (1, 2, 3, 4)

        self.assertRaises(tablib.InvalidDimensions, data.append, new_row)

    def test_set_headers_with_incorrect_dimension(self):
        """Verify headers correctly detects mismatch of number of
        headers and data.
        """

        data.append(self.john)

        def set_header_callable():
            data.headers = ['first_name']

        self.assertRaises(tablib.InvalidDimensions, set_header_callable)


    def test_add_column(self):
        """Verify adding column works with/without headers."""

        data.append(['kenneth'])
        data.append(['bessie'])

        new_col = ['reitz', 'monke']

        data.append_col(new_col)

        self.assertEqual(data[0], ('kenneth', 'reitz'))
        self.assertEqual(data.width, 2)

        # With Headers
        data.headers = ('fname', 'lname')
        new_col = [21, 22]
        data.append_col(new_col, header='age')

        self.assertEqual(data['age'], new_col)


    def test_add_column_no_data_no_headers(self):
        """Verify adding new column with no headers."""

        new_col = ('reitz', 'monke')

        data.append_col(new_col)

        self.assertEqual(data[0], tuple([new_col[0]]))
        self.assertEqual(data.width, 1)
        self.assertEqual(data.height, len(new_col))


    def test_add_column_with_header_ignored(self):
        """Verify append_col() ignores the header if data.headers has
        not previously been set
        """

        new_col = ('reitz', 'monke')

        data.append_col(new_col, header='first_name')

        self.assertEqual(data[0], tuple([new_col[0]]))
        self.assertEqual(data.width, 1)
        self.assertEqual(data.height, len(new_col))
        self.assertEqual(data.headers, None)


    def test_add_column_with_header_and_headers_only_exist(self):
        """Verify append_col() with header correctly detects mismatch when
        headers exist but there is no existing row data
        """

        data.headers = ['first_name']
        #no data

        new_col = ('allen')

        def append_col_callable():
            data.append_col(new_col, header='middle_name')

        self.assertRaises(tablib.InvalidDimensions, append_col_callable)


    def test_add_column_with_header_and_data_exists(self):
        """Verify append_col() works when headers and rows exists"""

        data.headers = self.headers
        data.append(self.john)

        new_col = [10];

        data.append_col(new_col, header='age')

        self.assertEqual(data.height, 1)
        self.assertEqual(data.width, len(self.john) + 1)
        self.assertEqual(data['age'], new_col)
        self.assertEqual(len(data.headers), len(self.headers) + 1)


    def test_add_callable_column(self):
        """Verify adding column with values specified as callable."""

        new_col = lambda x: x[0]

        self.founders.append_col(new_col, header='first_again')


    def test_header_slicing(self):
        """Verify slicing by headers."""

        self.assertEqual(self.founders['first_name'],
            [self.john[0], self.george[0], self.tom[0]])

        self.assertEqual(self.founders['last_name'],
            [self.john[1], self.george[1], self.tom[1]])

        self.assertEqual(self.founders['gpa'],
            [self.john[2], self.george[2], self.tom[2]])


    def test_get_col(self):
        """Verify getting columns by index"""

        self.assertEqual(
            self.founders.get_col(list(self.headers).index('first_name')),
            [self.john[0], self.george[0], self.tom[0]])

        self.assertEqual(
            self.founders.get_col(list(self.headers).index('last_name')),
            [self.john[1], self.george[1], self.tom[1]])

        self.assertEqual(
            self.founders.get_col(list(self.headers).index('gpa')),
            [self.john[2], self.george[2], self.tom[2]])


    def test_data_slicing(self):
        """Verify slicing by data."""

        # Slice individual rows
        self.assertEqual(self.founders[0], self.john)
        self.assertEqual(self.founders[:1], [self.john])
        self.assertEqual(self.founders[1:2], [self.george])
        self.assertEqual(self.founders[-1], self.tom)
        self.assertEqual(self.founders[3:], [])

        # Slice multiple rows
        self.assertEqual(self.founders[:], [self.john, self.george, self.tom])
        self.assertEqual(self.founders[0:2], [self.john, self.george])
        self.assertEqual(self.founders[1:3], [self.george, self.tom])
        self.assertEqual(self.founders[2:], [self.tom])


    def test_delete(self):
        """Verify deleting from dataset works."""

        # Delete from front of object
        del self.founders[0]
        self.assertEqual(self.founders[:], [self.george, self.tom])

        # Verify dimensions, width should NOT change
        self.assertEqual(self.founders.height, 2)
        self.assertEqual(self.founders.width, 3)

        # Delete from back of object
        del self.founders[1]
        self.assertEqual(self.founders[:], [self.george])

        # Verify dimensions, width should NOT change
        self.assertEqual(self.founders.height, 1)
        self.assertEqual(self.founders.width, 3)

        # Delete from invalid index
        self.assertRaises(IndexError, self.founders.__delitem__, 3)


    def test_csv_export(self):
        """Verify exporting dataset object as CSV."""

        # Build up the csv string with headers first, followed by each row
        csv = ''
        for col in self.headers:
            csv += col + ','

        csv = csv.strip(',') + '\r\n'

        for founder in self.founders:
            for col in founder:
                csv += str(col) + ','
            csv = csv.strip(',') + '\r\n'

        self.assertEqual(csv, self.founders.csv)


    def test_tsv_export(self):
        """Verify exporting dataset object as TSV."""

        # Build up the tsv string with headers first, followed by each row
        tsv = ''
        for col in self.headers:
            tsv += col + '\t'

        tsv = tsv.strip('\t') + '\r\n'

        for founder in self.founders:
            for col in founder:
                tsv += str(col) + '\t'
            tsv = tsv.strip('\t') + '\r\n'

        self.assertEqual(tsv, self.founders.tsv)


    def test_html_export(self):
        """HTML export"""

        html = markup.page()
        html.table.open()
        html.thead.open()

        html.tr(markup.oneliner.th(self.founders.headers))
        html.thead.close()

        for founder in self.founders:

            html.tr(markup.oneliner.td(founder))

        html.table.close()
        html = str(html)

        self.assertEqual(html, self.founders.html)


    def test_html_export_none_value(self):
        """HTML export"""

        html = markup.page()
        html.table.open()
        html.thead.open()

        html.tr(markup.oneliner.th(['foo','', 'bar']))
        html.thead.close()

        html.tr(markup.oneliner.td(['foo','', 'bar']))

        html.table.close()
        html = str(html)

        headers = ['foo', None, 'bar'];
        d = tablib.Dataset(['foo', None, 'bar'], headers=headers)

        self.assertEqual(html, d.html)


    def test_unicode_append(self):
        """Passes in a single unicode character and exports."""

        if is_py3:
            new_row = ('å', 'é')
        else:
            exec("new_row = (u'å', u'é')")


        data.append(new_row)

        data.json
        data.yaml
        data.csv
        data.tsv
        data.xls
        data.xlsx
        data.ods
        data.html


    def test_book_export_no_exceptions(self):
        """Test that various exports don't error out."""

        book = tablib.Databook()
        book.add_sheet(data)

        book.json
        book.yaml
        book.xls
        book.xlsx
        book.ods


    def test_json_import_set(self):
        """Generate and import JSON set serialization."""
        data.append(self.john)
        data.append(self.george)
        data.headers = self.headers

        _json = data.json

        data.json = _json

        self.assertEqual(json.loads(_json), json.loads(data.json))


    def test_json_import_book(self):
        """Generate and import JSON book serialization."""
        data.append(self.john)
        data.append(self.george)
        data.headers = self.headers

        book.add_sheet(data)
        _json = book.json

        book.json = _json

        self.assertEqual(json.loads(_json), json.loads(book.json))


    def test_yaml_import_set(self):
        """Generate and import YAML set serialization."""
        data.append(self.john)
        data.append(self.george)
        data.headers = self.headers

        _yaml = data.yaml

        data.yaml = _yaml

        self.assertEqual(_yaml, data.yaml)


    def test_yaml_import_book(self):
        """Generate and import YAML book serialization."""
        data.append(self.john)
        data.append(self.george)
        data.headers = self.headers

        book.add_sheet(data)
        _yaml = book.yaml

        book.yaml = _yaml

        self.assertEqual(_yaml, book.yaml)


    def test_csv_import_set(self):
        """Generate and import CSV set serialization."""
        data.append(self.john)
        data.append(self.george)
        data.headers = self.headers

        _csv = data.csv

        data.csv = _csv

        self.assertEqual(_csv, data.csv)


    def test_csv_import_set_with_spaces(self):
        """Generate and import CSV set serialization when row values have
        spaces."""
        data.append(('Bill Gates', 'Microsoft'))
        data.append(('Steve Jobs', 'Apple'))
        data.headers = ('Name', 'Company')

        _csv = data.csv

        data.csv = _csv

        self.assertEqual(_csv, data.csv)


    def test_csv_import_set_with_newlines(self):
        """Generate and import CSV set serialization when row values have
        newlines."""
        data.append(('Markdown\n=======',
                     'A cool language\n\nwith paragraphs'))
        data.append(('reStructedText\n==============',
                     'Another cool language\n\nwith paragraphs'))
        data.headers = ('title', 'body')

        _csv = data.csv

        data.csv = _csv

        self.assertEqual(_csv, data.csv)


    def test_tsv_import_set(self):
        """Generate and import TSV set serialization."""
        data.append(self.john)
        data.append(self.george)
        data.headers = self.headers

        _tsv = data.tsv

        data.tsv = _tsv

        self.assertEqual(_tsv, data.tsv)


    def test_csv_format_detect(self):
        """Test CSV format detection."""

        _csv = (
            '1,2,3\n'
            '4,5,6\n'
            '7,8,9\n'
        )
        _bunk = (
            '¡¡¡¡¡¡¡¡£™∞¢£§∞§¶•¶ª∞¶•ªº••ª–º§•†•§º¶•†¥ª–º•§ƒø¥¨©πƒø†ˆ¥ç©¨√øˆ¥≈†ƒ¥ç©ø¨çˆ¥ƒçø¶'
        )

        self.assertTrue(tablib.formats.csv.detect(_csv))
        self.assertFalse(tablib.formats.csv.detect(_bunk))


    def test_tsv_format_detect(self):
        """Test TSV format detection."""

        _tsv = (
            '1\t2\t3\n'
            '4\t5\t6\n'
            '7\t8\t9\n'
        )
        _bunk = (
            '¡¡¡¡¡¡¡¡£™∞¢£§∞§¶•¶ª∞¶•ªº••ª–º§•†•§º¶•†¥ª–º•§ƒø¥¨©πƒø†ˆ¥ç©¨√øˆ¥≈†ƒ¥ç©ø¨çˆ¥ƒçø¶'
        )

        self.assertTrue(tablib.formats.tsv.detect(_tsv))
        self.assertFalse(tablib.formats.tsv.detect(_bunk))


    def test_json_format_detect(self):
        """Test JSON format detection."""

        _json = '[{"last_name": "Adams","age": 90,"first_name": "John"}]'
        _bunk = (
            '¡¡¡¡¡¡¡¡£™∞¢£§∞§¶•¶ª∞¶•ªº••ª–º§•†•§º¶•†¥ª–º•§ƒø¥¨©πƒø†ˆ¥ç©¨√øˆ¥≈†ƒ¥ç©ø¨çˆ¥ƒçø¶'
        )

        self.assertTrue(tablib.formats.json.detect(_json))
        self.assertFalse(tablib.formats.json.detect(_bunk))


    def test_yaml_format_detect(self):
        """Test YAML format detection."""

        _yaml = '- {age: 90, first_name: John, last_name: Adams}'
        _tsv = 'foo\tbar'
        _bunk = (
            '¡¡¡¡¡¡---///\n\n\n¡¡£™∞¢£§∞§¶•¶ª∞¶•ªº••ª–º§•†•§º¶•†¥ª–º•§ƒø¥¨©πƒø†ˆ¥ç©¨√øˆ¥≈†ƒ¥ç©ø¨çˆ¥ƒçø¶'
        )

        self.assertTrue(tablib.formats.yaml.detect(_yaml))
        self.assertFalse(tablib.formats.yaml.detect(_bunk))
        self.assertFalse(tablib.formats.yaml.detect(_tsv))


    def test_auto_format_detect(self):
        """Test auto format detection."""

        _yaml = '- {age: 90, first_name: John, last_name: Adams}'
        _json = '[{"last_name": "Adams","age": 90,"first_name": "John"}]'
        _csv = '1,2,3\n4,5,6\n7,8,9\n'
        _tsv = '1\t2\t3\n4\t5\t6\n7\t8\t9\n'
        _bunk = '¡¡¡¡¡¡---///\n\n\n¡¡£™∞¢£§∞§¶•¶ª∞¶•ªº••ª–º§•†•§º¶•†¥ª–º•§ƒø¥¨©πƒø†ˆ¥ç©¨√øˆ¥≈†ƒ¥ç©ø¨çˆ¥ƒçø¶'

        self.assertEqual(tablib.detect(_yaml)[0], tablib.formats.yaml)
        self.assertEqual(tablib.detect(_csv)[0], tablib.formats.csv)
        self.assertEqual(tablib.detect(_tsv)[0], tablib.formats.tsv)
        self.assertEqual(tablib.detect(_json)[0], tablib.formats.json)
        self.assertEqual(tablib.detect(_bunk)[0], None)


    def test_transpose(self):
        """Transpose a dataset."""

        transposed_founders = self.founders.transpose()
        first_row = transposed_founders[0]
        second_row = transposed_founders[1]

        self.assertEqual(transposed_founders.headers,
                  ["first_name","John", "George", "Thomas"])
        self.assertEqual(first_row,
                   ("last_name","Adams", "Washington", "Jefferson"))
        self.assertEqual(second_row,
                   ("gpa",90, 67, 50))


    def test_row_stacking(self):
        """Row stacking."""

        to_join = tablib.Dataset(headers=self.founders.headers)

        for row in self.founders:
            to_join.append(row=row)

        row_stacked = self.founders.stack(to_join)

        for column in row_stacked.headers:

            original_data = self.founders[column]
            expected_data = original_data + original_data
            self.assertEqual(row_stacked[column], expected_data)


    def test_column_stacking(self):
        """Column stacking"""

        to_join = tablib.Dataset(headers=self.founders.headers)

        for row in self.founders:
            to_join.append(row=row)

        column_stacked = self.founders.stack_cols(to_join)

        for index, row in enumerate(column_stacked):

            original_data = self.founders[index]
            expected_data = original_data + original_data
            self.assertEqual(row, expected_data)

        self.assertEqual(column_stacked[0],
                   ("John", "Adams", 90, "John", "Adams", 90))


    def test_sorting(self):
        """Sort columns."""

        sorted_data = self.founders.sort(col="first_name")
        self.assertEqual(sorted_data.title, 'Founders')

        first_row = sorted_data[0]
        second_row = sorted_data[2]
        third_row = sorted_data[1]
        expected_first = self.founders[1]
        expected_second = self.founders[2]
        expected_third = self.founders[0]

        self.assertEqual(first_row, expected_first)
        self.assertEqual(second_row, expected_second)
        self.assertEqual(third_row, expected_third)


    def test_wipe(self):
        """Purge a dataset."""

        new_row = (1, 2, 3)
        data.append(new_row)

        # Verify width/data
        self.assertTrue(data.width == len(new_row))
        self.assertTrue(data[0] == new_row)

        data.wipe()
        new_row = (1, 2, 3, 4)
        data.append(new_row)
        self.assertTrue(data.width == len(new_row))
        self.assertTrue(data[0] == new_row)


    def test_formatters(self):
        """Confirm formatters are being triggered."""

        def _formatter(cell_value):
            return str(cell_value).upper()

        self.founders.add_formatter('last_name', _formatter)

        for name in [r['last_name'] for r in self.founders.dict]:
            self.assertTrue(name.isupper())

    def test_unicode_csv(self):
        """Check if unicode in csv export doesn't raise."""

        data = tablib.Dataset()

        if sys.version_info[0] > 2:
            data.append(['\xfc', '\xfd'])
        else:
            exec("data.append([u'\xfc', u'\xfd'])")


        data.csv

    def test_csv_column_select(self):
        """Build up a CSV and test selecting a column"""

        data = tablib.Dataset()
        data.csv = self.founders.csv

        headers = data.headers
        self.assertTrue(isinstance(headers[0], unicode))

        orig_first_name = self.founders[self.headers[0]]
        csv_first_name = data[headers[0]]
        self.assertEqual(orig_first_name, csv_first_name)


    def test_csv_column_delete(self):
        """Build up a CSV and test deleting a column"""

        data = tablib.Dataset()
        data.csv = self.founders.csv

        target_header = data.headers[0]
        self.assertTrue(isinstance(target_header, unicode))

        del data[target_header]

        self.assertTrue(target_header not in data.headers)

    def test_csv_column_sort(self):
        """Build up a CSV and test sorting a column by name"""

        data = tablib.Dataset()
        data.csv = self.founders.csv

        orig_target_header = self.founders.headers[1]
        target_header = data.headers[1]

        self.founders.sort(orig_target_header)
        data.sort(target_header)

        self.assertEqual(self.founders[orig_target_header], data[target_header])

    def test_unicode_renders_markdown_table(self):
        # add another entry to test right field width for
        # integer
        self.founders.append(('Old', 'Man', 100500))

        self.assertEqual(
            """
first_name|last_name |gpa   
----------|----------|------
John      |Adams     |90    
George    |Washington|67    
Thomas    |Jefferson |50    
Old       |Man       |100500
""".strip(),
            unicode(self.founders)
        )


    def test_databook_add_sheet_accepts_only_dataset_instances(self):
        class NotDataset(object):
            def append(self, item):
                pass

        dataset = NotDataset()
        dataset.append(self.john)

        self.assertRaises(tablib.InvalidDatasetType, book.add_sheet, dataset)


    def test_databook_add_sheet_accepts_dataset_subclasses(self):
        class DatasetSubclass(tablib.Dataset):
            pass

        # just checking if subclass of tablib.Dataset can be added to Databook
        dataset = DatasetSubclass()
        dataset.append(self.john)
        dataset.append(self.tom)

        try:
            book.add_sheet(dataset)
        except tablib.InvalidDatasetType:
            self.fail("Subclass of tablib.Dataset should be accepted by Databook.add_sheet")

if __name__ == '__main__':
    unittest.main()
