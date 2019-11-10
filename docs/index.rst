.. Tablib documentation master file, created by
   sphinx-quickstart on Tue Oct  5 15:25:21 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root ``toctree`` directive.

Tablib: Pythonic Tabular Datasets
=================================

Release v\ |version|. (:ref:`Installation <install>`)

.. Contents:
..
.. .. toctree::
..    :maxdepth: 2
..

.. Indices and tables
.. ==================
..
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`


Tablib is an `MIT Licensed <https://mit-license.org/>`_ format-agnostic tabular dataset library, written in Python.
It allows you to import, export, and manipulate tabular data sets.
Advanced features include segregation, dynamic columns, tags & filtering,
and seamless format import & export.

::

   >>> data = tablib.Dataset(headers=['First Name', 'Last Name', 'Age'])
   >>> for i in [('Kenneth', 'Reitz', 22), ('Bessie', 'Monke', 21)]:
   ...     data.append(i)


   >>> print(data.export('json'))
   [{"Last Name": "Reitz", "First Name": "Kenneth", "Age": 22}, {"Last Name": "Monke", "First Name": "Bessie", "Age": 21}]

   >>> print(data.export('yaml'))
   - {Age: 22, First Name: Kenneth, Last Name: Reitz}
   - {Age: 21, First Name: Bessie, Last Name: Monke}

   >>> data.export('xlsx')
   <redacted binary data>

   >>> data.export('df')
     First Name Last Name  Age
   0    Kenneth     Reitz   22
   1     Bessie     Monke   21


Testimonials
------------

`National Geographic <https://www.nationalgeographic.com/>`_,
`Digg, Inc <https://digg.com/>`_,
`Northrop Grumman <https://www.northropgrumman.com/>`_,
`Discovery Channel <https://dsc.discovery.com/>`_,
and `The Sunlight Foundation <https://sunlightfoundation.com/>`_ use Tablib internally.



**Greg Thorton**
   Tablib by @kennethreitz saved my life.
   I had to consolidate like 5 huge poorly maintained lists of domains and data.
   It was a breeze!

**Dave Coutts**
   It's turning into one of my most used modules of 2010.
   You really hit a sweet spot for managing tabular data with a minimal amount of code and effort.

**Joshua Ourisman**
   Tablib has made it so much easier to deal with the inevitable 'I want an Excel file!' requests from clients...

**Brad Montgomery**
    I think you nailed the "Python Zen" with tablib.
    Thanks again for an awesome lib!


User's Guide
------------

This part of the documentation, which is mostly prose, begins with some background information about Tablib, then focuses on step-by-step instructions for getting the most out of your datasets.

.. toctree::
   :maxdepth: 2

   intro

.. toctree::
   :maxdepth: 2

   install

.. toctree::
   :maxdepth: 2

   tutorial

.. toctree::
   :maxdepth: 2

   formats

.. toctree::
   :maxdepth: 2

   development


API Reference
-------------

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api
