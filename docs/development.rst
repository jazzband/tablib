.. _development:

Development
===========

Tablib is under active development, and contributors are welcome.

If you have a feature request, suggestion, or bug report, please open a new
issue on GitHub_. To submit patches, please send a pull request on GitHub_.

.. _GitHub: http://github.com/kennethreitz/tablib/



.. _design:

---------------------
Design Considerations
---------------------

Tablib was developed with a few :pep:`20` idioms in mind.

#. Beautiful is better than ugly.
#. Explicit is better than implicit.
#. Simple is better than complex.
#. Complex is better than complicated.
#. Readability counts.

A few other things to keep in mind:

#. Keep your code DRY.
#. Strive to be as simple (to use) as possible.

.. _scm:

--------------
Source Control
--------------


Tablib source is controlled with Git_, the lean, mean, distributed source
control machine.

The repository is publicly accessible.

    ``git clone git://github.com/kennethreitz/tablib.git``

The project is hosted on **GitHub**.


    GitHub:
        http://github.com/kennethreitz/tablib


Git Branch Structure
++++++++++++++++++++

Feature / Hotfix / Release branches follow a `Successful Git Branching Model`_ . Git-flow_ is a great tool for managing the repository. I highly recommend it.

``develop``
    The "next release" branch. Likely unstable.
``master``
    Current production release (|version|) on PyPi.

Each release is tagged.

When submitting patches, please place your feature/change in its own branch prior to opening a pull request on GitHub_.


.. _Git: http://git-scm.org
.. _`Successful Git Branching Model`: http://nvie.com/posts/a-successful-git-branching-model/
.. _git-flow: http://github.com/nvie/gitflow


.. _newformats:

------------------
Adding New Formats
------------------

Tablib welcomes new format additions! Format suggestions include:

* MySQL Dump


Coding by Convention
++++++++++++++++++++

Tablib features a micro-framework for adding format support. The easiest way to understand it is to use it. So, let's define our own format, named *xxx*.

1. Write a new format interface.

    :class:`tablib.core` follows a simple pattern for automatically utilizing your format throughout Tablib. Function names are crucial.

    Example **tablib/formats/_xxx.py**: ::

        title = 'xxx'

        def export_set(dset):
            ....
            # returns string representation of given dataset

        def export_book(dbook):
            ....
            # returns string representation of given databook

        def import_set(dset, in_stream):
            ...
            # populates given Dataset with given datastream

        def import_book(dbook, in_stream):
            ...
            # returns Databook instance

        def detect(stream):
            ...
            # returns True if given stream is parsable as xxx

.. admonition:: Excluding Support


    If the format excludes support for an import/export mechanism (*eg.* :class:`csv <tablib.Dataset.csv>` excludes :class:`Databook <tablib.Databook>` support), simply don't define the respective functions. Appropriate errors will be raised.

2.

    Add your new format module to the :class:`tablib.formats.available` tuple.

3.
    Add a mock property to the :class:`Dataset <tablib.Dataset>` class with verbose `reStructured Text`_ docstring. This alleviates IDE confusion, and allows for pretty auto-generated Sphinx_ documentation.

4. Write respective :ref:`tests <testing>`.

.. _testing:

--------------
Testing Tablib
--------------

Testing is crucial to Tablib's stability. This stable project is used in production by many companies and developers, so it is important to be certain that every version released is fully operational. When developing a new feature for Tablib, be sure to write proper tests for it as well.

When developing a feature for Tablib, the easiest way to test your changes for potential issues is to simply run the test suite directly. ::

	$ ./test_tablib.py


`Jenkins CI`_, amongst other tools, supports Java's xUnit testing report format. Nose_ allows us to generate our own xUnit reports.

Installing nose is simple. ::

	$ pip install nose

Once installed, we can generate our xUnit report with a single command. ::

	$ nosetests test_tablib.py --with-xunit

This will generate a **nosetests.xml** file, which can then be analyzed.

.. _Nose: https://github.com/nose-devs/nose



.. _jenkins:

----------------------
Continuous Integration
----------------------

Every commit made to the **develop** branch is automatically tested and inspected upon receipt with `Travis CI`_. If you have access to the main repository and broke the build, you will receive an email accordingly.

Anyone may view the build status and history at any time.

    https://travis-ci.org/kennethreitz/tablib

Additional reports will also be included here in the future, including :pep:`8` checks and stress reports for extremely large datasets.

.. _`Jenkins CI`: https://travis-ci.org/


.. _docs:

-----------------
Building the Docs
-----------------

Documentation is written in the powerful, flexible, and standard Python documentation format, `reStructured Text`_.
Documentation builds are powered by the powerful Pocoo project, Sphinx_. The :ref:`API Documentation <api>` is mostly documented inline throughout the module.

The Docs live in ``tablib/docs``. In order to build them, you will first need to install Sphinx. ::

	$ pip install sphinx


Then, to build an HTML version of the docs, simply run the following from the **docs** directory: ::

	$ make html

Your ``docs/_build/html`` directory will then contain an HTML representation of the documentation, ready for publication on most web servers.

You can also generate the documentation in **epub**, **latex**, **json**, *&c* similarly.

.. _`reStructured Text`: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org
.. _`GitHub Pages`: http://pages.github.com

----------

Make sure to check out the :ref:`API Documentation <api>`.
