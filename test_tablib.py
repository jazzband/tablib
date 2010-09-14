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

		self.assertTrue(data.width == len(new_row))

	def test_empty_append_with_headers(self):
		"""Verify append() correctly detects mismatch of number of
		headers and data
		"""
		data = tablib.Dataset()

		data.headers = ['first', 'second']
		new_row = (1, 2, 3, 4)

		self.assertRaises(tablib.InvalidDimensions, data.append, new_row)

	# def test_adding_header with (self):


if __name__ == '__main__':
	unittest.main()
