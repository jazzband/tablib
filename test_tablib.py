#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for Tablib."""

import unittest

import tablib


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

		self.founders = tablib.Dataset(headers=self.headers)
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


	def test_add_column(self):
		"""Verify adding column works with/without headers."""

		data.append(['kenneth'])
		data.append(['bessie'])

		new_col = ['reitz', 'monke']

		data.append(col=new_col)

		self.assertEquals(data[0], ('kenneth', 'reitz'))
		self.assertEquals(data.width, 2)

		# With Headers
		data.headers = ('fname', 'lname')
		new_col = ['age', 21, 22]
		data.append(col=new_col)

		self.assertEquals(data[new_col[0]], new_col[1:])


	def test_add_column_no_data_no_headers(self):
		"""Verify adding new column with no headers."""

		new_col = ('reitz', 'monke')

		data.append(col=new_col)

		self.assertEquals(data[0], tuple([new_col[0]]))
		self.assertEquals(data.width, 1)
		self.assertEquals(data.height, len(new_col))


	def test_add_column_no_data_with_headers(self):
		"""Verify adding new column with headers."""

		data.headers = ('first', 'last')

		new_col = ('age',)
		data.append(col=new_col)

		self.assertEquals(len(data.headers), 3)
		self.assertEquals(data.width, 3)

		new_col = ('foo', 'bar')

		self.assertRaises(tablib.InvalidDimensions, data.append, col=new_col)

	def test_add_callable_column(self):
		"""Verify adding column with values specified as callable."""
		new_col = ['first_again', lambda x: x[0]]
		self.founders.append(col=new_col)

		self.assertTrue(map(lambda x: x[0] == x[-1], self.founders))


	def test_header_slicing(self):
		"""Verify slicing by headers."""

		self.assertEqual(self.founders['first_name'],
						[self.john[0], self.george[0], self.tom[0]])
		self.assertEqual(self.founders['last_name'],
						[self.john[1], self.george[1], self.tom[1]])
		self.assertEqual(self.founders['gpa'],
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
		"""Verify exporting dataset object as CSV."""

		# Build up the csv string with headers first, followed by each row
		tsv = ''
		for col in self.headers:
			tsv += col + '\t'

		tsv = tsv.strip('\t') + '\r\n'

		for founder in self.founders:
			for col in founder:
				tsv += str(col) + '\t'
			tsv = tsv.strip('\t') + '\r\n'

		self.assertEqual(tsv, self.founders.tsv)

	def test_unicode_append(self):
		"""Passes in a single unicode charecter and exports."""

		new_row = ('å', 'é')
		data.append(new_row)

		data.json
		data.yaml
		data.csv
		data.tsv
		data.xls

 
	def test_book_export_no_exceptions(self):
		"""Test that varoius exports don't error out."""

		book = tablib.Databook()
		book.add_sheet(data)

		book.json
		book.yaml
		book.xls


	def test_json_import_set(self):
		"""Generate and import JSON set serialization."""
		data.append(self.john)
		data.append(self.george)
		data.headers = self.headers

		_json = data.json

		data.json = _json

		self.assertEqual(_json, data.json)


	def test_json_import_book(self):
		"""Generate and import JSON book serialization."""
		data.append(self.john)
		data.append(self.george)
		data.headers = self.headers

		book.add_sheet(data)
		_json = book.json

		book.json = _json

		self.assertEqual(_json, book.json)


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
		_bunk = (
			'¡¡¡¡¡¡---///\n\n\n¡¡£™∞¢£§∞§¶•¶ª∞¶•ªº••ª–º§•†•§º¶•†¥ª–º•§ƒø¥¨©πƒø†ˆ¥ç©¨√øˆ¥≈†ƒ¥ç©ø¨çˆ¥ƒçø¶'
		)

		self.assertTrue(tablib.formats.yaml.detect(_yaml))
		self.assertFalse(tablib.formats.yaml.detect(_bunk))


	def test_auto_format_detect(self):
		"""Test auto format detection."""

		_yaml = '- {age: 90, first_name: John, last_name: Adams}'
		_json = '[{"last_name": "Adams","age": 90,"first_name": "John"}]'
		_csv = '1,2,3\n4,5,6\n7,8,9\n'
		_bunk = '¡¡¡¡¡¡---///\n\n\n¡¡£™∞¢£§∞§¶•¶ª∞¶•ªº••ª–º§•†•§º¶•†¥ª–º•§ƒø¥¨©πƒø†ˆ¥ç©¨√øˆ¥≈†ƒ¥ç©ø¨çˆ¥ƒçø¶'

		self.assertEqual(tablib.detect(_yaml)[0], tablib.formats.yaml)
		self.assertEqual(tablib.detect(_csv)[0], tablib.formats.csv)
		self.assertEqual(tablib.detect(_json)[0], tablib.formats.json)
		self.assertEqual(tablib.detect(_bunk)[0], None)


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
	
		
if __name__ == '__main__':
	unittest.main()
