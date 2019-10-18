.. _quickstart:

==========
Quickstart
==========


Eager to get started?
This page gives a good introduction in how to get started with Tablib.
This assumes you already have Tablib installed.
If you do not, head over to the :ref:`Installation <install>` section.

First, make sure that:

* Tablib is :ref:`installed <install>`
* Tablib is :ref:`up-to-date <updates>`


Let's get started with some simple use cases and examples.



------------------
Creating a Dataset
------------------


A :class:`Dataset <tablib.Dataset>` is nothing more than what its name implies—a set of data.

Creating your own instance of the :class:`tablib.Dataset` object is simple. ::

    data = tablib.Dataset()

You can now start filling this :class:`Dataset <tablib.Dataset>` object with data.

.. admonition:: Example Context

    From here on out, if you see ``data``, assume that it's a fresh 
    :class:`Dataset <tablib.Dataset>` object.



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

You can get a nice, Pythonic view of the dataset at any time with :class:`Dataset.dict`::

    >>> data.dict
    [('Kenneth', 'Reitz'), ('Bessie', 'Monke')]



--------------
Adding Headers
--------------


It's time to enhance our :class:`Dataset` by giving our columns some titles.
To do so, set :class:`Dataset.headers`. ::

    data.headers = ['First Name', 'Last Name']

Now our data looks a little different. ::

    >>> data.dict
    [{'Last Name': 'Reitz', 'First Name': 'Kenneth'},
     {'Last Name': 'Monke', 'First Name': 'Bessie'}]




--------------
Adding Columns
--------------


Now that we have a basic :class:`Dataset` in place, let's add a column of **ages** to it. ::

    data.append_col([22, 20], header='Age')

Let's view the data now. ::

    >>> data.dict
    [{'Last Name': 'Reitz', 'First Name': 'Kenneth', 'Age': 22},
     {'Last Name': 'Monke', 'First Name': 'Bessie', 'Age': 20}]

It's that easy.


--------------
Importing Data
--------------
Creating a :class:`tablib.Dataset` object by importing a pre-existing file is simple. ::

   imported_data = Dataset().load(open('data.csv').read())

This detects what sort of data is being passed in, and uses an appropriate formatter to do the import. So you can import from a variety of different file types.

--------------
Exporting Data
--------------

Tablib's killer feature is the ability to export your :class:`Dataset` objects into a number of formats.

**Comma-Separated Values** ::

    >>> data.export('csv')
    Last Name,First Name,Age
    Reitz,Kenneth,22
    Monke,Bessie,20

**JavaScript Object Notation** ::

    >>> data.export('json')
    [{"Last Name": "Reitz", "First Name": "Kenneth", "Age": 22}, {"Last Name": "Monke", "First Name": "Bessie", "Age": 20}]


**YAML Ain't Markup Language** ::

    >>> data.export('yaml')
    - {Age: 22, First Name: Kenneth, Last Name: Reitz}
    - {Age: 20, First Name: Bessie, Last Name: Monke}


**Microsoft Excel** ::

    >>> data.export('xls')
    <redacted binary data>


**Pandas DataFrame** ::

    >>> data.export('df')
      First Name Last Name  Age
    0    Kenneth     Reitz   22
    1     Bessie     Monke   21


------------------------
Selecting Rows & Columns
------------------------


You can slice and dice your data, just like a standard Python list. ::

    >>> data[0]
    ('Kenneth', 'Reitz', 22)


If we had a set of data consisting of thousands of rows,
it could be useful to get a list of values in a column.
To do so, we access the :class:`Dataset` as if it were a standard Python dictionary.  ::

    >>> data['First Name']
    ['Kenneth', 'Bessie']

You can also access the column using its index. ::

    >>> data.headers
    ['Last Name', 'First Name', 'Age']
    >>> data.get_col(1)
    ['Kenneth', 'Bessie']

Let's find the average age. ::

    >>> ages = data['Age']
    >>> float(sum(ages)) / len(ages)
    21.0



-----------------------
Removing Rows & Columns
-----------------------

It's easier than you could imagine. Delete a column::

    >>> del data['Col Name']

Delete a range of rows::

    >>> del data[0:12]


==============
Advanced Usage
==============

This part of the documentation services to give you an idea that are otherwise hard to extract from the :ref:`API Documentation <api>`

And now for something completely different.


.. _dyncols:

---------------
Dynamic Columns
---------------

.. versionadded:: 0.8.3

Thanks to Josh Ourisman, Tablib now supports adding dynamic columns.
A dynamic column is a single callable object (*e.g.* a function).

Let's add a dynamic column to our :class:`Dataset` object.
In this example, we have a function that generates a random grade for our students. ::

    import random

    def random_grade(row):
        """Returns a random integer for entry."""
        return (random.randint(60,100)/100.0)

    data.append_col(random_grade, header='Grade')

Let's have a look at our data. ::

    >>> data.export('yaml')
    - {Age: 22, First Name: Kenneth, Grade: 0.6, Last Name: Reitz}
    - {Age: 20, First Name: Bessie, Grade: 0.75, Last Name: Monke}


Let's remove that column.  ::

    >>> del data['Grade']


When you add a dynamic column, the first argument that is passed in to the given callable is the current data row.
You can use this to perform calculations against your data row.

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

    >>> data.export('yaml')
    - {Age: 22, First Name: Kenneth, Gender: Male, Last Name: Reitz}
    - {Age: 20, First Name: Bessie, Gender: Female, Last Name: Monke}


.. _tags:

----------------------------
Filtering Datasets with Tags
----------------------------

.. versionadded:: 0.9.0


When constructing a :class:`Dataset` object,
you can add tags to rows by specifying the ``tags`` parameter.
This allows you to filter your :class:`Dataset` later.
This can be useful to separate rows of data based on arbitrary criteria
(*e.g.* origin) that you don't want to include in your :class:`Dataset`.

Let's tag some students. ::

    students = tablib.Dataset()

    students.headers = ['first', 'last']

    students.rpush(['Kenneth', 'Reitz'], tags=['male', 'technical'])
    students.rpush(['Bessie', 'Monke'], tags=['female', 'creative'])

Now that we have extra meta-data on our rows, we can easily filter our :class:`Dataset`. Let's just see Male students. ::


    >>> students.filter(['male']).yaml
    - {first: Kenneth, Last: Reitz}

It's that simple. The original :class:`Dataset` is untouched.

Open an Excel Workbook and read first sheet
-------------------------------------------

To open an Excel 2007 and later workbook with a single sheet (or a workbook with multiple sheets but you just want the first sheet), use the following:

data = tablib.Dataset()
data.xlsx = open('my_excel_file.xlsx', 'rb').read()
print(data)

Excel Workbook With Multiple Sheets
------------------------------------

When dealing with a large number of :class:`Datasets <Dataset>` in spreadsheet format,
it's quite common to group multiple spreadsheets into a single Excel file, known as a Workbook.
Tablib makes it extremely easy to build workbooks with the handy :class:`Databook` class.

Let's say we have 3 different :class:`Datasets <Dataset>`.
All we have to do is add them to a :class:`Databook` object... ::

    book = tablib.Databook((data1, data2, data3))

... and export to Excel just like :class:`Datasets <Dataset>`. ::

    with open('students.xls', 'wb') as f:
        f.write(book.xls)

The resulting ``students.xls`` file will contain a separate spreadsheet for each :class:`Dataset` object in the :class:`Databook`.

.. admonition:: Binary Warning

    Make sure to open the output file in binary mode.


.. _separators:

----------
Separators
----------

.. versionadded:: 0.8.2

When constructing a spreadsheet,
it's often useful to create a blank row containing information on the upcoming data. So,

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
    tests.append_separator('Daniel\'s Scores')

    for test_row in daniel_tests:
       tests.append(test_row)

    # Susie's Tests
    tests.append_separator('Susie\'s Scores')

    for test_row in suzie_tests:
       tests.append(test_row)

    # Write spreadsheet to disk
    with open('grades.xls', 'wb') as f:
        f.write(tests.export('xls'))

The resulting **tests.xls** will have the following layout:


    Daniel's Scores:
        * '11/24/09', 'Math 101 Mid-term Exam', 56.
        * '05/24/10', 'Math 101 Final Exam', 62.

    Suzie's Scores:
        * '11/24/09', 'Math 101 Mid-term Exam', 56.
        * '05/24/10', 'Math 101 Final Exam', 62.



.. admonition:: Format Support

    At this time, only :class:`Excel <Dataset.xls>` output supports separators.

----

Now, go check out the :ref:`API Documentation <api>` or begin :ref:`Tablib Development <development>`.
