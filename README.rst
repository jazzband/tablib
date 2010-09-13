Tablib: format-agnostic tabular dataset library
===============================================

::

	_____         ______  ___________ ______  
	__  /_______ ____  /_ ___  /___(_)___  /_ 
	_  __/_  __ `/__  __ \__  / __  / __  __ \
	/ /_  / /_/ / _  /_/ /_  /  _  /  _  /_/ /
	\__/  \__,_/  /_.___/ /_/   /_/   /_.___/



Tablib is a format-agnostic tabular dataset library, written in Python. 

Output formats supported:

- Excel
- JSON
- YAML
- CSV

At this time, Tablib supports the **export** of it's powerful Dataset object instances into any of the above formats. Import is underway.

Note that tablib *purposefully* excludes XML support. It always will.


Usage
-----

    
Populate fresh data files: ::
    
    headers = ('first_name', 'last_name', 'gpa')

    data = [
        ('John', 'Adams', 90),
        ('George', 'Washington', 67)
    ]
    
    data = tablib.Dataset(*data, headers=headers)


Intelligently add new rows: ::

    >>> data.append(('Henry', 'Ford', 83))
    
Slice rows:  ::

    >>> print data[:2]
    [('John', 'Adams', 90), ('George', 'Washington', 67)]
    

Slice columns by header: ::

    >>> print data['first_name']
    ['John', 'George', 'Henry']

Easily delete rows: ::

    >>> del data[1]

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

	>>> open('people.xls').write(data.xls)
		
It's that easy.
	
    
Installation
------------

To install tablib, simply: ::

	$ pip install tablib
	
Or, if you absolutely must: ::

	$ easy_install tablib
    

Contribute
----------

If you'd like to contribute, simply fork `the repository`_, commit your changes, and send a pull request. Make sure you add yourself to AUTHORS_.


Roadmap
-------
- Add ability to add/remove full columns
- Import datasets from CSV, JSON, YAML
- Release CLI Interface
- Auto-detect import format
- Add possible other exports (SQL?)
- Possibly plugin-ify format architecture
- Plugin support

.. _`the repository`: http://github.com/kennethreitz/tablib
.. _AUTHORS: http://github.com/kennethreitz/tablib/blob/master/AUTHORS