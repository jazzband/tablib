History
-------

0.11.5 (2017-06-13)
+++++++++++++++++++

- Use ``yaml.safe_load`` for importing yaml.

0.11.4 (2017-01-23)
+++++++++++++++++++

- Use built-in `json` package if available
- Support Python 3.5+ in classifiers

** Bugfixes **

- Fixed textual representation for Dataset with no headers
- Handle decimal types

0.11.3 (2016-02-16)
+++++++++++++++++++

- Release fix.

0.11.2 (2016-02-16)
+++++++++++++++++++

**Bugfixes**

- Fix export only formats.
- Fix for xlsx output.

0.11.1 (2016-02-07)
+++++++++++++++++++

**Bugfixes**

- Fixed packaging error on Python 3.


0.11.0 (2016-02-07)
+++++++++++++++++++

**New Formats!**

- Added LaTeX table export format (``Dataset.latex``).
- Support for dBase (DBF) files (``Dataset.dbf``).

**Improvements**

- New import/export interface (``Dataset.export()``, ``Dataset.load()``).
- CSV custom delimiter support (``Dataset.export('csv', delimiter='$')``).
- Adding ability to remove duplicates to all rows in a dataset (``Dataset.remove_duplicates()``).
- Added a mechanism to avoid ``datetime.datetime`` issues when serializing data.
- New ``detect_format()`` function (mostly for internal use).
- Update the vendored unicodecsv to fix ``None`` handling.
- Only freeze the headers row, not the headers columns (xls).

**Breaking Changes**

- ``detect()`` function removed.

**Bugfixes**

- Fix XLSX import.
- Bugfix for ``Dataset.transpose().transpose()``.


0.10.0 (2014-05-27)
+++++++++++++++++++

* Unicode Column Headers
* ALL the bugfixes!

0.9.11 (2011-06-30)
+++++++++++++++++++

* Bugfixes

0.9.10 (2011-06-22)
+++++++++++++++++++

* Bugfixes

0.9.9 (2011-06-21)
++++++++++++++++++

* Dataset API Changes
* ``stack_rows`` => ``stack``, ``stack_columns`` => ``stack_cols``
* column operations have their own methods now (``append_col``, ``insert_col``)
* List-style ``pop()``
* Redis-style ``rpush``, ``lpush``, ``rpop``, ``lpop``, ``rpush_col``, and ``lpush_col``

0.9.8 (2011-05-22)
++++++++++++++++++

* OpenDocument Spreadsheet support (.ods)
* Full Unicode TSV support


0.9.7 (2011-05-12)
++++++++++++++++++

* Full XLSX Support!
* Pickling Bugfix
* Compat Module


0.9.6 (2011-05-12)
++++++++++++++++++

* ``seperators`` renamed to ``separators``
* Full unicode CSV support


0.9.5 (2011-03-24)
++++++++++++++++++

* Python 3.1, Python 3.2 Support (same code base!)
* Formatter callback support
* Various bug fixes



0.9.4 (2011-02-18)
++++++++++++++++++

* Python 2.5 Support!
* Tox Testing for 2.5, 2.6, 2.7
* AnyJSON Integrated
* OrderedDict support
* Caved to community pressure (spaces)


0.9.3 (2011-01-31)
++++++++++++++++++

* Databook duplication leak fix.
* HTML Table output.
* Added column sorting.


0.9.2 (2010-11-17)
++++++++++++++++++

* Transpose method added to Datasets.
* New frozen top row in Excel output.
* Pickling support for Datasets and Rows.
* Support for row/column stacking.


0.9.1 (2010-11-04)
++++++++++++++++++

* Minor reference shadowing bugfix.


0.9.0 (2010-11-04)
++++++++++++++++++

* Massive documentation update!
* Tablib.org!
* Row tagging and Dataset filtering!
* Column insert/delete support
* Column append API change (header required)
* Internal Changes (Row object and use thereof)


0.8.5 (2010-10-06)
++++++++++++++++++

* New import system. All dependencies attempt to load from site-packages,
  then fallback on tenderized modules.


0.8.4 (2010-10-04)
++++++++++++++++++

* Updated XLS output: Only wrap if '\\n' in cell.


0.8.3 (2010-10-04)
++++++++++++++++++

* Ability to append new column passing a callable
  as the value that will be applied to every row.


0.8.2 (2010-10-04)
++++++++++++++++++

* Added alignment wrapping to written cells.
* Added separator support to XLS.


0.8.1 (2010-09-28)
++++++++++++++++++

* Packaging Fix


0.8.0 (2010-09-25)
++++++++++++++++++

* New format plugin system!
* Imports! ELEGANT Imports!
* Tests. Lots of tests.


0.7.1 (2010-09-20)
++++++++++++++++++

* Reverting methods back to properties.
* Windows bug compensated in documentation.


0.7.0 (2010-09-20)
++++++++++++++++++

* Renamed DataBook Databook for consistency.
* Export properties changed to methods (XLS filename / StringIO bug).
* Optional Dataset.xls(path='filename') support (for writing on windows).
* Added utf-8 on the worksheet level.


0.6.4 (2010-09-19)
++++++++++++++++++

* Updated unicode export for XLS.
* More exhaustive unit tests.


0.6.3 (2010-09-14)
++++++++++++++++++
* Added Dataset.append() support for columns.


0.6.2 (2010-09-13)
++++++++++++++++++
* Fixed Dataset.append() error on empty dataset.
* Updated Dataset.headers property w/ validation.
* Added Testing Fixtures.

0.6.1 (2010-09-12)
++++++++++++++++++

* Packaging hotfixes.


0.6.0 (2010-09-11)
++++++++++++++++++

* Public Release.
* Export Support for XLS, JSON, YAML, and CSV.
* DataBook Export for XLS, JSON, and YAML.
* Python Dict Property Support.
