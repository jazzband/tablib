.. _quickstart:
Quickstart
==========

.. module:: tablib


Eager to get started? This page gives a good introduction in how to get started with Tablib. This assumes you already have Tablib installed. If you do not, head over to the :ref:`Installation <install>` section.

First, make sure that:

* Tablib is :ref:`installed <install>`
* Tablib is :ref:`up-to-date <updates>`


Lets gets started with some simple use cases and examples.

Creating a Dataset
------------------

A :class:`Dataset <tablib.Dataset>` is nothing more than what its name implies—a set of data.

Creating your own instance of the :class:`tablib.Dataset` object is simple. ::

    data = tablib.Dataset()
    
You can now start filling this :class:`Dataset <tablib.Dataset>` object with data.

.. admonition:: Example Context
     
     From here on out, if you see ``data``, assume that it's a fresh :class:`Dataset <tablib.Dataset>` object.


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


Adding Headers
--------------

It's time enhance our :class:`Dataset` by giving our columns some titles. To do so, set :class:`Dataset.headers`. ::

    data.headers = ['First Name', 'Last Name']

Let's view the data in YAML this time. ::

    >>> data.yaml
    - {First Name: Kenneth, Last Name: Reitz}
    - {First Name: Bessie, Last Name: Monke}
    

Adding Columns 
--------------

Now that we have a basic :class:`Dataset` in place, let's add a column of **ages** to it. ::

    data.append(col=['Age', 22, 20])
    
Let's view the data in CSV this time. ::

    >>> data.csv
    Last Name,First Name,Age 
    Reitz,Kenneth,22 
    Monke,Bessie,20

It's that easy.

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



Dynamic Columns
---------------

.. versionadded:: 0.8.3

Thanks to Josh Ourisman, Tablib now supports adding dynamic columns. For now, this is only supported on :class:`Dataset` objects that have no defined :class:`headers <Dataset.headers>`.

Let's save our headers for later. ::

    _headers = list(data.headers)
    data.headers = None

test ::

    import random
    
    def random_grade(*args):
        """Returns a random integer for entry."""
        return (random.randint(60,100)/100.0)
    
    data.append(col=[random_grade])


::
    >>> data.yaml
    - [Reitz, Kenneth, 22, 0.83]
    - [Monke, Bessie, 21, 0.73]

Now we can add our headers back.
::
    >>> data.headers = _headers + ['Random']

Let's delete that column. 

::
    >>> del data['Grade']


.. _seperators:

Seperators
----------



Transposition
-------------

Thanks to Luca Beltrame, :class:`Dataset` objects 
::

    data.transpose()


Shortcuts
---------

Population upon instantiation.


Now, go check out the :ref:`API Documentation <api>` or begin :ref:`Tablib Development <development>`.