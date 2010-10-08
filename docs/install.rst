.. _install:

Installation
============

This part of the documentation covers all the interfaces of Tablib.  For
parts where Tablib depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


Installing Tablib
-----------------

To install Tablib, it only takes one simple command. ::

	$ pip install tablib

Or, if you must: ::

	$ easy_install tablib
	
But, you really shouldn't do that. 

Speed Extentions
----------------

Tablib is partially dependent on the **pyyaml**, **simplejson**, and **xlwt** modules. To reduce installation issues, fully integrated versions of all required libraries are included in Tablib. 

However, if performance is important to you (and it should be), you should install **simplejson** and **pyyaml** with C extentions from PyPi. ::

	$ pip install PyYAML

If you're using Python 2.6+, the built-in **json** module is already optimized and in use. If you're using Python 2.5 (currently unsupported), you should also install the **simplejson** module. ::

	$ pip install simplejson

.. If you're using a Python < 2.6, you can speed up JSON 


Pythons Supported
-----------------

At this time, only the following Python platforms are officially supported: 

* Python 2.6
* Python 2.7

Support for other Pythons will be rolled out soon.




Virtualenv
----------

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


Staying Updated
---------------

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.