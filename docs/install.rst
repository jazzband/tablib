.. _install:
Installation
============

This part of the documentation covers the installation of Tablib. The first step to using any software package is getting it properly installed. Please read this section carefully, or you may miss out on some nice  :ref:`speed enhancements <peed-extentions>`.


.. _installing:

-----------------
Installing Tablib
-----------------

Distribute & Pip
----------------

Installing Tablib is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install tablib

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install tablib

But, you really `shouldn't do that <http://www.pip-installer.org/en/latest/index.html#pip-compared-to-easy-install>`_.



Cheeseshop Mirror
-----------------

If the Cheeseshop is down, you can also install Requests from Kenneth Reitz's personal `Cheeseshop mirror <pip.kreitz.co/>`_::

    $ pip install -i http://pip.kreitz.co/simple tablib




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


.. _speed-extentions:
Speed Extentions
----------------

.. versionadded:: 0.8.5

Tablib is partially dependent on the **pyyaml**, **simplejson**, and **xlwt** modules. To reduce installation issues, fully integrated versions of all required libraries are included in Tablib.

However, if performance is important to you (and it should be), you can install  **pyyaml** with C extentions from PyPi. ::

    $ pip install PyYAML

If you're using Python 2.5, you should also install the **simplejson** module (pip will do this for you). If you're using Python 2.6+, the built-in **json** module is already optimized and in use. ::

    $ pip install simplejson



.. _updates:
Staying Updated
---------------

The latest version of Tablib will always be available here:

* PyPi: http://pypi.python.org/pypi/tablib/
* GitHub: http://github.com/kennethreitz/tablib/

When a new version is available, upgrading is simple::

    $ pip install tablib --upgrade


Now, go get a :ref:`Quick Start <quickstart>`.