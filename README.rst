Tablib: format-agnostic tabular dataset library
===============================================

::

	_____         ______  ___________ ______  
	__  /_______ ____  /_ ___  /___(_)___  /_ 
	_  __/_  __ `/__  __ \__  / __  / __  __ \
	/ /_  / /_/ / _  /_/ /_  /  _  /  _  /_/ /
	\__/  \__,_/  /_.___/ /_/   /_/   /_.___/



Tablib is a format-agnostic tabular dataset library, written in Python. 
It is a full python module which doubles as a CLI application for quick
dataset conversions. 

Formats supported:

- JSON
- YAML
- Excel
- CSV

At this time, Tablib supports the **export** of it's powerful Dataset object instances into any of the above formats. Import is underway.

Please note that tablib *purposefully* excludes XML support. It always will.


Features
--------

    
Populate fresh data files: ::
    
    headers = ('first_name', 'last_name', 'gpa')

    data = [
        ('John', 'Adams', 4.0),
        ('George', 'Washington', 2.6),
        ('Henry', 'Ford', 2.3)
    ]
    
    data = tablib.Dataset(*data, headers=headers)

    # Establish file location and save
    data.save('test.xls')
    

Intelligently add new rows: ::

    data.append('Bob', 'Dylan', 3.2)
    
    print data.headers
    # >>> ('first_name', 'last_name', 'gpa')
    

Slice rows:  ::

    print data[0:1]
    # >>> [('John', 'Adams', 4.0), ('George', 'Washington', 2.6)]
    

Slice columns by header: ::

    print data['first_name']
    # >>> ['John', 'George', 'Henry']


Manipulate rows by index: ::

    del data[0]
    print data[0:1]
    # >>> [('George', 'Washington', 2.6), ('Henry', 'Ford', 2.3)]
    
    


Roadmap
-------
- Import datasets from CSV, JSON, YAML
- Auto-detect import format
- Plugin support