#!/usr/bin/env python
# encoding: utf-8


from helpers import *
# from core import Parse

from packages import opster


opts = (
	('v', 'version', False, 'Report tabbed version'),
	('', 'to', False, 'Output format')
)


@opster.command(options=opts, usage='[FILE] [--to] [FILE]')
def start(**opts):
	""" Converts dataset formats """
	
	print opts
	
	opts = Object(**opts)