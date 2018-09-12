.. _install:
Installation
============

This part of the documentation covers the installation of Tablib. The first step to using any software package is getting it properly installed.


.. _installing:

-----------------
Installing Tablib
-----------------

Distribute & Pip
----------------

Of course, the recommended way to install Tablib is with `pip <http://www.pip-installer.org/>`_::

    $ pip install tablib[pandas]


-------------------
Download the Source
-------------------

You can also install tablib from source. The latest release (|version|) is available from GitHub.

* tarball_
* zipball_

.. _
Once you have a copy of the source, you can embed it in your Python package, or install it into your site-packages easily. ::

    $ python setup.py install


To download the full source history from Git, see :ref:`Source Control <scm>`.

.. _tarball: http://github.com/kennethreitz/tablib/tarball/master
.. _zipball: http://github.com/kennethreitz/tablib/zipball/master


.. _updates:
Staying Updated
---------------

The latest version of Tablib will always be available here:

* PyPi: http://pypi.python.org/pypi/tablib/
* GitHub: http://github.com/kennethreitz/tablib/

When a new version is available, upgrading is simple::

    $ pip install tablib --upgrade


Now, go get a :ref:`Quick Start <quickstart>`.
