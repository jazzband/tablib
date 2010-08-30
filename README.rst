Tabbed: format-agnostic tabular dataset library
===============================================

::

    _____         ______  ______        _________
    __  /_______ ____  /_ ___  /_ _____ ______  /
    _  __/_  __ `/__  __ \__  __ \_  _ \_  __  / 
    / /_  / /_/ / _  /_/ /_  /_/ //  __// /_/ /  
    \__/  \__,_/  /_.___/ /_.___/ \___/ \__,_/   

*Tabbed is under active documentation-driven development.*


Tabbed is a format-agnostic tabular dataset library, written in Python. 
It is a full python module which doubles as a CLI application for quick
dataset conversions. 

Formats supported:

- JSON
- YAML
- Excel
- CSV
- HTML

Please note that tabbed *purposefully* excludes XML support. It always will.


Features
--------

Convert datafile formats via API: ::

    tablib.source(filename='data.csv').export('data.json')


Convert datafile formats via CLI: ::

    $ tabbed data.csv data.json
    
Convert data formats via CLI pipe interface: ::
    
    $ curl http://domain.dev/dataset.json | tabbed --to excel | gist -p
    
    
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

    data.add_row('Bob', 'Dylan')
    # >>> Warning: Existing column count is 3
    
    print data.headers
    # >>> ('first_name', 'last_name', 'gpa')
    

Slice rows:  ::

    print data[0:1]
    # >>> [('John', 'Adams', 4.0), ('George', 'Washington', 2.6)]
    

.. Slice columns by header: ::
.. 
..     print data['first_name']
..     # >>> ['John', 'George', 'Henry']
..     

Manipulate rows by index: ::

    del data[0]
    print data[0:1]
    # >>> [('George', 'Washington', 2.6), ('Henry', 'Ford', 2.3)]
    
    # Update saved file
    data.save()
    

Export to various formats: ::

    # Save copy as CSV
    data.export('backup.csv')