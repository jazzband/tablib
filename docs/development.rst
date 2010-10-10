.. _development:

Development
===========

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

.. _future:
Future of Tablib
----------------

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


.. _design:
Design Considerations
---------------------

Tablib was developed with a few `The Zen of Python`_ idioms in mind.

#. Beautiful is better than ugly.
#. Explicit is better than implicit.
#. Simple is better than complex.
#. Complex is better than complicated.
#. Readability counts.

It strives to be as simple to use as possible.

.. _git:
Source Control
--------------

Git. 
GitHub.
git.kennethreitz.com

Git Flow

.. _newformats:
Adding New Formats
------------------

Don't. 


.. _testing:
Testing Tablib
--------------
Testing is crucial to Tablib's stability. This stable project is used in production by many companies and developers, so it is important to be certian that every version released is fully operational. When developing a new feature for Tablib, be sure to write proper tests for it as well.


Running the Test Suite
++++++++++++++++++++++

When developing a feature for Tablib, the easiest way to test your changes for potential issues is to simply run the test suite directly. ::

	$ ./test_tablib.py


`Hudson CI`_, amongst other tools, supports Java's xUnit testing report format. Nose_ allows us to generate our own xUnit reports. 

Installing nose is simple. ::

	$ pip install nose

Once installed, we can generate our xUnit report with a single command. ::

	$ nosetests test_tablib.py --with-xunit

This will generate a **nosetests.xml** file, which can then be analyzed.

.. _Nose: http://somethingaboutorange.com/mrl/projects/nose/

Extending the Test Suite
++++++++++++++++++++++++

Example: ::

	import tablib.formats.sql.test_sql


.. _hudson:
Continuous Integration
----------------------

Every commit made to the **develop** branch is automatically tested and inspected upon receipt with `Hudson CI`_. If you have access to the main respository and broke the build, you will receive an email accordingly. 

Anyone may view the build status and history at any time.

    http://git.kennethreitz.com/ci/


If you are trustworthy and plan to contribute to tablib on a regular basis, please contact `Kenneth Reitz`_ to get an account on the Hudson Server. 


Additional reports will also be included here in the future, including PEP 8 checks and stress reports for extremely large datasets.

.. _`Hudson CI`: http://hudson.dev.java.net
.. _`Kenneth Reitz`: http://kennethreitz.com/contact-me/


.. _docs:
Building the Docs
-----------------

Documentation is written in the powerful, flexible, and standard Python documentation format, `reStructured Text`_. 
Documentation builds are powered by powerful Pocoo project, Sphinx_. The :ref:`API Documentation <api>` is mostly documented inline throught the module.

The Docs live in ``tablib/docs``. In order to build them, you will first need to install Sphinx. ::

	$ pip install sphinx
	

Then, to build an HTML version of the docs, simply run the following from the **docs** directory: ::

	$ make html	

Your ``docs/_build/html`` directory will then contain an HTML representation of the documentation, ready for publication on most web servers.

You can also generate the documentation in **ebpub**, **latex**, **json**, *&c* similarly.

.. admonition:: GitHub Pages

	To push the documentation up to `GitHub Pages`_, you will first need to run `sphinx-to-github`_ against your ``docs/_build/html`` directory. 
	
	GitHub Pages are powered by an HTML generation system called Jeckyl_, which is configured to ignore files and folders that begin with "``_``" (*ie.* **_static**).
	





	 and `sphinx-to-github`_. ::

	Installing sphinx-to-github is simple. ::

		$ pip install sphinx-to-github

	Running it against the docs is even simpler. ::

		$ sphinx-to-github _build/html
	
	Move the resulting files to the **gh-pages** branch of your repository, and push it up to GitHub. 

.. _`reStructured Text`: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org
.. _`GitHub Pages`: http://pages.github.com
.. _Jeckyl: http://github.com/mojombo/jekyll
.. _`sphinx-to-github`: http://github.com/michaeljones/sphinx-to-github

Make sure to check out the :ref:`API Documentation <api>`.