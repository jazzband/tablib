#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for tablib"""

import unittest

import tablib


class TablibTestCase(unittest.TestCase):
	"""Tablib test cases"""

	def setUp(self):
		"""setup"""
		pass

	def tearDown(self):
		"""teardown"""
		pass

	def test_empty_append(self):
		"""Verify append() correctly adds tuple with no headers"""
		data = tablib.Dataset()

		new_row = (1, 2, 3)
		data.append(new_row)

		# Verify width/data
		self.assertTrue(data.width == len(new_row))
		self.assertTrue(data[0] == new_row)

	def test_empty_append_with_headers(self):
		"""Verify append() correctly detects mismatch of number of
		headers and data
		"""
		data = tablib.Dataset()

		data.headers = ['first', 'second']
		new_row = (1, 2, 3, 4)

		self.assertRaises(tablib.InvalidDimensions, data.append, new_row)

	def test_header_slicing(self):
		"""Verify slicing by headers"""

		headers = ('first_name', 'last_name', 'gpa')

		data = [
			('John', 'Adams', 90),
			('George', 'Washington', 67)
		]

		data = tablib.Dataset(*data, headers=headers)

		# Slice by headers
		self.assertEqual(data['first_name'], ['John', 'George'])
		self.assertEqual(data['last_name'], ['Adams', 'Washington'])
		self.assertEqual(data['gpa'], [90, 67])

	# def test_adding_header with (self):


if __name__ == '__main__':
	unittest.main()
