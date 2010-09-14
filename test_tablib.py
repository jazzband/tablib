#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import tablib

class TablibTestCase(unittest.TestCase):
	def setUp(self):
		global data
		data = tablib.Dataset()

	def tearDown(self):
		pass

	
	def test_empty_append(self):
		new_row = (1,2,3)
		data.append(new_row)

		self.assertTrue(data.width == len(new_row))


	def test_empty_append_with_headers(self):

		data.headers = ['first', 'second']
		new_row = (1,2,3,4)
		
		self.assertRaises(tablib.InvalidDimensions, data.append, new_row)


	def test_add_column(self):
		# No Headers

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

		# no headers

		new_col = ('reitz', 'monke')

		data.append(col=new_col)

		self.assertEquals(data[0], tuple([new_col[0]]))
		self.assertEquals(data.width, 1)
		self.assertEquals(data.height, len(new_col))


	def test_add_column_no_data_with_headers(self):

		# no headers

		data.headers = ('first', 'last')

		new_col = ('age',)
		data.append(col=new_col)

		self.assertEquals(len(data.headers), 3)
		self.assertEquals(data.width, 3)

		new_col = ('foo', 'bar')
		
		self.assertRaises(tablib.InvalidDimensions, data.append, col=new_col)

	def tuple_check(self):
		data.append(col=(1,2,3))
		
if __name__ == '__main__':
	unittest.main()