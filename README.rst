Tablib: format-agnostic tabular dataset library
===============================================

.. image:: https://travis-ci.org/kennethreitz/tablib.svg?branch=develop
    :target: https://travis-ci.org/kennethreitz/tablib

::

	_____         ______  ___________ ______
	__  /_______ ____  /_ ___  /___(_)___  /_
	_  __/_  __ `/__  __ \__  / __  / __  __ \
	/ /_  / /_/ / _  /_/ /_  /  _  /  _  /_/ /
	\__/  \__,_/  /_.___/ /_/   /_/   /_.___/



Tablib is a format-agnostic tabular dataset library, written in Python.

Output formats supported:

- Excel (Sets + Books)
- JSON (Sets + Books)
- YAML (Sets + Books)
- HTML (Sets)
- TSV (Sets)
- CSV (Sets)

Note that tablib *purposefully* excludes XML support. It always will. (Note: This is a joke. Pull requests are welcome.)

Overview
--------

`tablib.Dataset()`
	A Dataset is a table of tabular data. It may or may not have a header row. They can be build and manipulated as raw Python datatypes (Lists of tuples|dictionaries). Datasets can be imported from JSON, YAML, and CSV; they can be exported to XLSX, XLS, ODS, JSON, YAML, CSV, TSV, and HTML.

`tablib.Databook()`
	A Databook is a set of Datasets. The most common form of a Databook is an Excel file with multiple spreadsheets. Databooks can be imported from JSON and YAML; they can be exported to XLSX, XLS, ODS, JSON, and YAML.

Usage
-----


Populate fresh data files: ::

    headers = ('first_name', 'last_name')

    data = [
        ('John', 'Adams'),
        ('George', 'Washington')
    ]

    data = tablib.Dataset(*data, headers=headers)


Intelligently add new rows: ::

    >>> data.append(('Henry', 'Ford'))

Intelligently add new columns: ::

    >>> data.append_col((90, 67, 83), header='age')

Slice rows:  ::

    >>> print data[:2]
    [('John', 'Adams', 90), ('George', 'Washington', 67)]


Slice columns by header: ::

    >>> print data['first_name']
    ['John', 'George', 'Henry']

Easily delete rows: ::

    >>> del data[1]

Exports
-------

Drumroll please...........

JSON!
+++++
::

	>>> print data.json
	[
	  {
	    "last_name": "Adams",
	    "age": 90,
	    "first_name": "John"
	  },
	  {
	    "last_name": "Ford",
	    "age": 83,
	    "first_name": "Henry"
	  }
	]


YAML!
+++++
::

	>>> print data.yaml
	- {age: 90, first_name: John, last_name: Adams}
	- {age: 83, first_name: Henry, last_name: Ford}

CSV...
++++++
::

	>>> print data.csv
	first_name,last_name,age
	John,Adams,90
	Henry,Ford,83

EXCEL!
++++++
::

	>>> with open('people.xls', 'wb') as f:
	...     f.write(data.xls)

It's that easy.


Installation
------------

To install tablib, simply: ::

	$ pip install tablib

Or, if you absolutely must: ::

	$ easy_install tablib

Contribute
----------

If you'd like to contribute, simply fork `the repository`_, commit your
changes to the **develop** branch (or branch off of it), and send a pull
request. Make sure you add yourself to AUTHORS_.




.. _`the repository`: http://github.com/kennethreitz/tablib
.. _AUTHORS: http://github.com/kennethreitz/tablib/blob/master/AUTHORS
