# History

## 3.4.0 (2023-03-24)

### Improvements

- Move setup to `pyproject.toml` (#542)
- xlsx export: remove redundant code (#541)
- xlsx export: support escape of formulae (#540)
- Add &lt;tbody&gt; tags to HTML output (#539)
- Check for type list and improve error msg (#524)

### Bugfixes

- Fix bug when yaml file is empty (#535)
- Fix linting issues raised by Flake8 (#536)
 
## 3.3.0 (2022-12-10)

### Improvements

- Add support for Python 3.11 (#525).
- ODS export: integers/floats/decimals are exported as numbers (#527).

## 3.2.1 (2022-04-09)

### Bugfixes

- Support solo CR in text input imports (#518).

## 3.2.0 (2022-01-27)

### Changes

- Dropped Python 3.6 support (#513).

### Bugfixes

- Corrected order of arguments to a regex call in `safe_xlsx_sheet_title` (#510).

## 3.1.0 (2021-10-26)

### Improvements

- Add support for Python 3.10 (#504).
- The csv, xls, and xlsx formats gained support for the `skip_lines` keyword
  argument for their `import_set()` method to be able to skip the nth first
  lines of a read file (#497).

### Bugfixes

- Avoided mutable parameter defaults (#494).
- Specify build backend for editable installs (#501).
- Doubled sample size passed to `csv.Sniffer()` in `_csv.detect()` (#503).

## 3.0.0 (2020-12-05)

### Breaking changes

- Dropped Python 3.5 support.
- JSON-exported data is no longer forced to ASCII characters.
- YAML-exported data is no longer forced to ASCII characters.

### Improvements

- Added Python 3.9 support.
- Added read_only option to xlsx file reader (#482).

### Bugfixes

- Prevented crash in rst export with only-space strings (#469).

## 2.0.0 (2020-05-16)

### Breaking changes

- The `Row.lpush/rpush` logic was reversed. `lpush` was appending while `rpush`
  and `append` were prepending. This was fixed (reversed behavior). If you
  counted on the broken behavior, please update your code (#453).

### Bugfixes

- Fixed minimal openpyxl dependency version to 2.6.0 (#457).
- Dates from xls files are now read as Python datetime objects (#373).
- Allow import of "ragged" xlsx files (#465).

### Improvements

- When importing an xlsx file, Tablib will now read cell values instead of formulas (#462).

## 1.1.0 (2020-02-13)

### Deprecations

- Upcoming breaking change in Tablib 2.0.0: the `Row.lpush/rpush` logic is reversed.
  `lpush` is appending while `rpush` and `append` are prepending. The broken behavior
  will remain in Tablib 1.x and will be fixed (reversed) in Tablib 2.0.0 (#453). If you
  count on the broken behavior, please update your code when you upgrade to Tablib 2.x.

### Improvements

- Tablib is now able to import CSV content where not all rows have the same
  length. Missing columns on any line receive the empty string (#226).

## 1.0.0 (2020-01-13)

### Breaking changes

- Dropped Python 2 support
- Dependencies are now all optional. To install `tablib` as before with all
  possible supported formats, run `pip install tablib[all]`

### Improvements

- Formats can now be dynamically registered through the
  `tablib.formats.registry.refister` API (#256).
- Tablib methods expecting data input (`detect_format`, `import_set`,
  `Dataset.load`, `Databook.load`) now accepts file-like objects in addition
  to raw strings and bytestrings (#440).

### Bugfixes

- Fixed a crash when exporting an empty string with the ReST format (#368)
- Error cells from imported .xls files contain now the error string (#202)

## 0.14.0 (2019-10-19)

### Deprecations

- The 0.14.x series will be the last to support Python 2

### Breaking changes

- Dropped Python 3.4 support

### Improvements

- Added Python 3.7 and 3.8 support
- The project is now maintained by the Jazzband team, https://jazzband.co
- Improved format autodetection and added autodetection for the odf format.
- Added search to all documentation pages
- Open xlsx workbooks in read-only mode (#316)
- Unpin requirements
- Only install backports.csv on Python 2

### Bugfixes

- Fixed `DataBook().load` parameter ordering (first stream, then format).
- Fixed a regression for xlsx exports where non-string values were forced to
  strings (#314)
- Fixed xlsx format detection (which was often detected as `xls` format)

## 0.13.0 (2019-03-08)

- Added reStructuredText output capability (#336)
- Added Jira output capability
- Stopped calling openpyxl deprecated methods (accessing cells, removing sheets)
  (openpyxl minimal version is now 2.4.0)
- Fixed a circular dependency issue in JSON output (#332)
- Fixed Unicode error for the CSV export on Python 2 (#215)
- Removed usage of optional `ujson` (#311)
- Dropped Python 3.3 support

## 0.12.1 (2017-09-01)

- Favor `Dataset.export(<format>)` over `Dataset.<format>` syntax in docs
- Make Panda dependency optional

## 0.12.0 (2017-08-27)

- Add initial Panda DataFrame support
- Dropped Python 2.6 support

## 0.11.5 (2017-06-13)

- Use `yaml.safe_load` for importing yaml.

## 0.11.4 (2017-01-23)

- Use built-in `json` package if available
- Support Python 3.5+ in classifiers

### Bugfixes

- Fixed textual representation for Dataset with no headers
- Handle decimal types

## 0.11.3 (2016-02-16)

- Release fix.

## 0.11.2 (2016-02-16)

### Bugfixes

- Fix export only formats.
- Fix for xlsx output.

## 0.11.1 (2016-02-07)

### Bugfixes

- Fixed packaging error on Python 3.


## 0.11.0 (2016-02-07)

### New Formats!

- Added LaTeX table export format (`Dataset.latex`).
- Support for dBase (DBF) files (`Dataset.dbf`).

### Improvements

- New import/export interface (`Dataset.export()`, `Dataset.load()`).
- CSV custom delimiter support (`Dataset.export('csv', delimiter='$')`).
- Adding ability to remove duplicates to all rows in a dataset (`Dataset.remove_duplicates()`).
- Added a mechanism to avoid `datetime.datetime` issues when serializing data.
- New `detect_format()` function (mostly for internal use).
- Update the vendored unicodecsv to fix `None` handling.
- Only freeze the headers row, not the headers columns (xls).

### Breaking Changes

- `detect()` function removed.

### Bugfixes

- Fix XLSX import.
- Bugfix for `Dataset.transpose().transpose()`.


## 0.10.0 (2014-05-27)

* Unicode Column Headers
* ALL the bugfixes!

## 0.9.11 (2011-06-30)

* Bugfixes

## 0.9.10 (2011-06-22)

* Bugfixes

## 0.9.9 (2011-06-21)

* Dataset API Changes
* `stack_rows` => `stack`, `stack_columns` => `stack_cols`
* column operations have their own methods now (`append_col`, `insert_col`)
* List-style `pop()`
* Redis-style `rpush`, `lpush`, `rpop`, `lpop`, `rpush_col`, and `lpush_col`

## 0.9.8 (2011-05-22)

* OpenDocument Spreadsheet support (.ods)
* Full Unicode TSV support


## 0.9.7 (2011-05-12)

* Full XLSX Support!
* Pickling Bugfix
* Compat Module


## 0.9.6 (2011-05-12)

* `seperators` renamed to `separators`
* Full unicode CSV support


## 0.9.5 (2011-03-24)

* Python 3.1, Python 3.2 Support (same code base!)
* Formatter callback support
* Various bug fixes



## 0.9.4 (2011-02-18)

* Python 2.5 Support!
* Tox Testing for 2.5, 2.6, 2.7
* AnyJSON Integrated
* OrderedDict support
* Caved to community pressure (spaces)


## 0.9.3 (2011-01-31)

* Databook duplication leak fix.
* HTML Table output.
* Added column sorting.


## 0.9.2 (2010-11-17)

* Transpose method added to Datasets.
* New frozen top row in Excel output.
* Pickling support for Datasets and Rows.
* Support for row/column stacking.


## 0.9.1 (2010-11-04)

* Minor reference shadowing bugfix.


## 0.9.0 (2010-11-04)

* Massive documentation update!
* Tablib.org!
* Row tagging and Dataset filtering!
* Column insert/delete support
* Column append API change (header required)
* Internal Changes (Row object and use thereof)


## 0.8.5 (2010-10-06)

* New import system. All dependencies attempt to load from site-packages,
  then fallback on tenderized modules.


## 0.8.4 (2010-10-04)

* Updated XLS output: Only wrap if '\\n' in cell.


## 0.8.3 (2010-10-04)

* Ability to append new column passing a callable
  as the value that will be applied to every row.


## 0.8.2 (2010-10-04)

* Added alignment wrapping to written cells.
* Added separator support to XLS.


## 0.8.1 (2010-09-28)

* Packaging Fix


## 0.8.0 (2010-09-25)

* New format plugin system!
* Imports! ELEGANT Imports!
* Tests. Lots of tests.


## 0.7.1 (2010-09-20)

* Reverting methods back to properties.
* Windows bug compensated in documentation.


## 0.7.0 (2010-09-20)

* Renamed DataBook Databook for consistency.
* Export properties changed to methods (XLS filename / StringIO bug).
* Optional Dataset.xls(path='filename') support (for writing on windows).
* Added utf-8 on the worksheet level.


## 0.6.4 (2010-09-19)

* Updated unicode export for XLS.
* More exhaustive unit tests.


## 0.6.3 (2010-09-14)

* Added Dataset.append() support for columns.


## 0.6.2 (2010-09-13)

* Fixed Dataset.append() error on empty dataset.
* Updated Dataset.headers property w/ validation.
* Added Testing Fixtures.

## 0.6.1 (2010-09-12)

* Packaging hotfixes.


## 0.6.0 (2010-09-11)

* Public Release.
* Export Support for XLS, JSON, YAML, and CSV.
* DataBook Export for XLS, JSON, and YAML.
* Python Dict Property Support.
