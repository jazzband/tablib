#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import tablib

class TablibTestCase(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_empty_append(self):
		data = tablib.Dataset()
		new_row = (1,2,3)
		data.append(new_row)
		assert data.width == len(new_row)
		
	


if __name__ == '__main__':
	unittest.main()