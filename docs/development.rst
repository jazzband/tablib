.. _development:

Development
===========

Tablib is under active development, and contributors are welcome.

If you have a feature request, suggestion, or bug report, please open a new
issue on GitHub_. To submit patches, please send a pull request on GitHub_.

.. _GitHub: https://github.com/jazzband/tablib/



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

.. code-block:: console

    git clone git://github.com/jazzband/tablib.git

The project is hosted on **GitHub**.

    GitHub:
        https://github.com/jazzband/tablib


Git Branch Structure
++++++++++++++++++++

Feature / Hotfix / Release branches follow a `Successful Git Branching Model`_ .
Git-flow_ is a great tool for managing the repository. I highly recommend it.

``master``
    Current production release (|version|) on PyPi.

Each release is tagged.

When submitting patches, please place your feature/change in its own branch prior to opening a pull request on GitHub_.


.. _Git: https://git-scm.org
.. _`Successful Git Branching Model`: https://nvie.com/posts/a-successful-git-branching-model/
.. _git-flow: https://github.com/nvie/gitflow


.. _newformats:

------------------
Adding New Formats
------------------

Tablib welcomes new format additions! Format suggestions include:

* MySQL Dump


Coding by Convention
++++++++++++++++++++

Tablib features a micro-framework for adding format support.
The easiest way to understand it is to use it.
So, let's define our own format, named *xxx*.

From version 1.0, Tablib formats are class-based and can be dynamically
registered.

1. Write your custom format class::

    class MyXXXFormatClass:
        title = 'xxx'

        @classmethod
        def export_set(cls, dset):
            ....
            # returns string representation of given dataset

        @classmethod
        def export_book(cls, dbook):
            ....
            # returns string representation of given databook

        @classmethod
        def import_set(cls, dset, in_stream):
            ...
            # populates given Dataset with given datastream

        @classmethod
        def import_book(cls, dbook, in_stream):
            ...
            # returns Databook instance

        @classmethod
        def detect(cls, stream):
            ...
            # returns True if given stream is parsable as xxx

   .. admonition:: Excluding Support

       If the format excludes support for an import/export mechanism (*e.g.* 
       :class:`csv <tablib.Dataset.csv>` excludes 
       :class:`Databook <tablib.Databook>` support),
       simply don't define the respective class methods.
       Appropriate errors will be raised.

2. Register your class::

    from tablib.formats import registry

    registry.register('xxx', MyXXXFormatClass())

3. From then on, you should be able to use your new custom format as if it were
a built-in Tablib format, e.g. using ``dataset.export('xxx')`` will use the 
``MyXXXFormatClass.export_set`` method.

.. _testing:

--------------
Testing Tablib
--------------

Testing is crucial to Tablib's stability.
This stable project is used in production by many companies and developers,
so it is important to be certain that every version released is fully operational.
When developing a new feature for Tablib, be sure to write proper tests for it as well.

When developing a feature for Tablib,
the easiest way to test your changes for potential issues is to simply run the test suite directly.

.. code-block:: console

    $ tox

----------------------
Continuous Integration
----------------------

Every pull request is automatically tested and inspected upon receipt with `GitHub Actions`_.
If you broke the build, you will receive an email accordingly.

Anyone may view the build status and history at any time.

    https://github.com/jazzband/tablib/actions

Additional reports will also be included here in the future, including :pep:`8` checks and stress reports for extremely large datasets.

.. _`GitHub Actions`: https://github.com/jazzband/tablib/actions


.. _docs:

-----------------
Building the Docs
-----------------

Documentation is written in the powerful, flexible,
and standard Python documentation format, `reStructured Text`_.
Documentation builds are powered by the powerful Pocoo project, Sphinx_.
The :ref:`API Documentation <api>` is mostly documented inline throughout the module.

The Docs live in ``tablib/docs``.
In order to build them, you will first need to install Sphinx.

.. code-block:: console

    $ pip install sphinx


Then, to build an HTML version of the docs, simply run the following from the ``docs`` directory:

.. code-block:: console

    $ make html

Your ``docs/_build/html`` directory will then contain an HTML representation of the documentation,
ready for publication on most web servers.

You can also generate the documentation in **epub**, **latex**, **json**, *&c* similarly.

.. _`reStructured Text`: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org
.. _`GitHub Pages`: https://pages.github.com

----------

Make sure to check out the :ref:`API Documentation <api>`.
