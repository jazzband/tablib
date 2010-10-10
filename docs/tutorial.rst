.. _quickstart:

==========
Quickstart
==========


.. module:: tablib


Eager to get started? This page gives a good introduction in how to get started with Tablib. This assumes you already have Tablib installed. If you do not, head over to the :ref:`Installation <install>` section.

First, make sure that:

* Tablib is :ref:`installed <install>`
* Tablib is :ref:`up-to-date <updates>`


Lets gets started with some simple use cases and examples.



------------------
Creating a Dataset
------------------


A :class:`Dataset <tablib.Dataset>` is nothing more than what its name implies—a set of data.

Creating your own instance of the :class:`tablib.Dataset` object is simple. ::

    data = tablib.Dataset()
    
You can now start filling this :class:`Dataset <tablib.Dataset>` object with data.

.. admonition:: Example Context
     
     From here on out, if you see ``data``, assume that it's a fresh :class:`Dataset <tablib.Dataset>` object.



-----------
Adding Rows
-----------


Let's say you want to collect a simple list of names. ::

    # collection of names
    names = ['Kenneth Reitz', 'Bessie Monke']

    for name in names:
        # split name appropriately
        fname, lname = name.split()
        
        # add names to Dataset
        data.append([fname, lname])

You can get a nice, Pythonic view of the dataset at any time with :class:`Dataset.dict`.

    >>> data.dict
    [('Kenneth', 'Reitz'), ('Bessie', 'Monke')]



--------------
Adding Headers
--------------


It's time enhance our :class:`Dataset` by giving our columns some titles. To do so, set :class:`Dataset.headers`. ::

    data.headers = ['First Name', 'Last Name']

Now our data looks a little different. ::

    >>> data.dict
    [{'Last Name': 'Reitz', 'First Name': 'Kenneth'}, {'Last Name': 'Monke', 'First Name': 'Bessie'}]
    



--------------
Adding Columns 
--------------


Now that we have a basic :class:`Dataset` in place, let's add a column of **ages** to it. ::

    data.append(col=['Age', 22, 20])
    
Let's view the data now. ::

    >>> data.dict
    [{'Last Name': 'Reitz', 'First Name': 'Kenneth', 'Age': 22}, {'Last Name': 'Monke', 'First Name': 'Bessie', 'Age': 21}]

It's that easy.


--------------
Exporting Data
--------------

Tablib's killer feature is the ability to export your :class:`Dataset` objects into a number of formats.

**Comma-Seperated Values** ::

    >>> data.csv
    Last Name,First Name,Age 
    Reitz,Kenneth,22 
    Monke,Bessie,21

**JavaScript Object Notation** ::

    >>> data.json
    [{"Last Name": "Reitz", "First Name": "Kenneth", "Age": 22}, {"Last Name": "Monke", "First Name": "Bessie", "Age": 21}]


**YAML Ain't Markup Language** ::

    >>> data.yaml
    - {Age: 22, First Name: Kenneth, Last Name: Reitz}
    - {Age: 21, First Name: Bessie, Last Name: Monke}
    

**Microsoft Excel** ::

    >>> data.xls
    <censored binary data>


------------------------
Selecting Rows & Columns
------------------------


You can slice and dice your data, just like a standard Python list. ::

    >>> data[0]
    ('Kenneth', 'Reitz', 22)


If we had a set of data consisting of thousands of rows, it could be useful to get a list of values in a column.
To do so, we access the :class:`Dataset` as if it were a standard Python dictionary.  ::

    >>> data['First Name']
    ['Kenneth', 'Bessie']

Let's find the average age. ::

    >>> ages = data['Age']
    >>> float(sum(ages)) / len(ages)
    21.0



-----------------------
Removing Rows & Columns
-----------------------

::

    >>> del data['Col Name']

::

    >>> del data[0:12]

Fucking easy.



==============
Advanced Usage
==============


This part of the documentation services to give you an idea that are otherwise hard to extract from the :ref:`API Documentation <api>`

And now for something completely different.


---------------
Dynamic Columns
---------------

.. versionadded:: 0.8.3

Thanks to Josh Ourisman, Tablib now supports adding dynamic columns. A dynamic column is a single callable object (*ie.* a function).
For now, this is only supported on :class:`Dataset` objects that have no defined :class:`headers <Dataset.headers>`.

So, let's save our headers for later, then remove them. ::

    _headers = list(data.headers)
    data.headers = None


We can now add a dynamic column to our :class:`Dataset` object. In this example, we have a function that generates a random grade for our students. ::

    import random
    
    def random_grade(row):
        """Returns a random integer for entry."""
        return (random.randint(60,100)/100.0)
    
    data.append(col=[random_grade])


Now add the headers back, with our new column. ::

    >>> data.headers = _headers + ['Random']

Let's have a look at our data. ::

    >>> data.yaml
    - {Age: 22, First Name: Kenneth, Grade: 0.6, Last Name: Reitz}
    - {Age: 21, First Name: Bessie, Grade: 0.75, Last Name: Monke}


Let's remove that column.  ::

    >>> del data['Grade']


When you add a dynamic column, the first argument that is passed in to the given callable is the current data row. You can use this to perform calculations against your data row. 

For example, we can use the data available in the row to guess the gender of a student. ::

    def guess_gender(row):
        """Calculates gender of given student data row."""
        m_names = ('Kenneth', 'Mike', 'Yuri')
        f_names = ('Bessie', 'Samantha', 'Heather')
        
        name = row[0]
        
        if name in m_names:
            return 'Male'
        elif name in f_names:
            return 'Female'
        else:
            return 'Unknown'

Adding this function to our dataset as a dynamic column would result in: ::

    >>> data.yaml
    - {Age: 22, First Name: Kenneth, Gender: Male, Last Name: Reitz}
    - {Age: 21, First Name: Bessie, Gender: Female, Last Name: Monke}





Excel Workbook With Multiple Sheets
------------------------------------ 

:class:`Databook` 

::

    book = tablib.Databook([data, data, data])

::

    with open('students.xls', 'wb') as f:
        f.write(book.xls)

The resulting **students.xls** file will contain a seperate spreadsheet for each :class:`Dataset` object in the :class:`Databook`.

.. admonition:: Binary Warning

    Make sure to open the output file in binary mode.


.. _seperators:

----------
Seperators
----------

.. versionadded:: 0.8.2

When, it's often useful to create a blank row containing information on the upcomming data. So, 



::

    daniel_tests = [
        ('11/24/09', 'Math 101 Mid-term Exam', 56.),
        ('05/24/10', 'Math 101 Final Exam', 62.)
    ]
    
    suzie_tests = [
        ('11/24/09', 'Math 101 Mid-term Exam', 56.),
        ('05/24/10', 'Math 101 Final Exam', 62.)
    ]
    
    # Create new dataset
    tests = tablib.Dataset()
    tests.headers = ['Date', 'Test Name', 'Grade']

    # Daniel's Tests
    tests.append_seperator('Daniel\'s Scores')

    for test_row in daniel_tests:
       tests.append(test_row)

    # Susie's Tests
    tests.append_seperator('Susie\'s Scores')

    for test_row in suzie_tests:
       tests.append(test_row)

    # Write spreadsheet to disk
    with open('grades.xls', 'wb') as f:
        f.write(tests.xls)

The resulting **tests.xls** will have the following layout: 


    Daniel's Scores:
        * '11/24/09', 'Math 101 Mid-term Exam', 56.
        * '05/24/10', 'Math 101 Final Exam', 62.

    Suzie's Scores:
        * '11/24/09', 'Math 101 Mid-term Exam', 56.
        * '05/24/10', 'Math 101 Final Exam', 62.



.. admonition:: Format Support

    At this time, only :class:`Excel <Dataset.xls>` output supports seperators.
    
----

Now, go check out the :ref:`API Documentation <api>` or begin :ref:`Tablib Development <development>`.