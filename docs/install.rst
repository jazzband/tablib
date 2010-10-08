.. _install:

Installation
============

This part of the documentation covers the installation of Tablib. The first step to using any software package is getting it properly installed. Please read this section carefully, or you may miss out on some nice  :ref:`speed enhancments <speed>`..

Installing Tablib
-----------------

To install Tablib, it only takes one simple command. ::

	$ pip install tablib

Or, if you must: ::

	$ easy_install tablib
	
But, you really shouldn't do that. 

.. _speed:

Speed Extentions
----------------

.. versionadded:: 0.8.5

Tablib is partially dependent on the **pyyaml**, **simplejson**, and **xlwt** modules. To reduce installation issues, fully integrated versions of all required libraries are included in Tablib. 

However, if performance is important to you (and it should be), you can install  **pyyaml** with C extentions from PyPi. ::

	$ pip install PyYAML

If you're using Python 2.5 (currently unsupported), you should also install the **simplejson** module. If you're using Python 2.6+, the built-in **json** module is already optimized and in use. ::

	$ pip install simplejson




Pythons Supported
-----------------

At this time, the following Python platforms are officially supported: 

* Python 2.6
* Python 2.7

Support for other Pythons will be rolled out soon.



Staying Updated
---------------

The latest version of Tablib will always be available here: 

* PyPi: http://pypi.python.org/pypi/tablib/
* GitHub: http://github.com/kennethreitz/tablib/

When a new version is available, upgrading is simple. ::

	$ pip install tablib --upgrade

