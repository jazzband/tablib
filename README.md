# Tablib: format-agnostic tabular dataset library

[![Jazzband](https://jazzband.co/static/img/badge.svg)](https://jazzband.co/)
[![Build Status](https://travis-ci.org/jazzband/tablib.svg?branch=master)](https://travis-ci.org/jazzband/tablib)
[![codecov](https://codecov.io/gh/jazzband/tablib/branch/master/graph/badge.svg)](https://codecov.io/gh/jazzband/tablib)

    _____         ______  ___________ ______
    __  /_______ ____  /_ ___  /___(_)___  /_
    _  __/_  __ `/__  __ \__  / __  / __  __ \
    / /_  / /_/ / _  /_/ /_  /  _  /  _  /_/ /
    \__/  \__,_/  /_.___/ /_/   /_/   /_.___/


Tablib is a format-agnostic tabular dataset library, written in Python.

Output formats supported:

- Excel (Sets + Books)
- JSON (Sets + Books)
- YAML (Sets + Books)
- Pandas DataFrames (Sets)
- HTML (Sets)
- Jira (Sets)
- TSV (Sets)
- ODS (Sets)
- CSV (Sets)
- DBF (Sets)

Note that tablib *purposefully* excludes XML support. It always will. (Note: This is a
joke. Pull requests are welcome.)


## Overview

`tablib.Dataset()`

A Dataset is a table of tabular data.
It may or may not have a header row.
They can be build and manipulated as raw Python datatypes (Lists of tuples|dictionaries).
Datasets can be imported from JSON, YAML, DBF, and CSV;
they can be exported to XLSX, XLS, ODS, JSON, YAML, DBF, CSV, TSV, and HTML.

`tablib.Databook()`

A Databook is a set of Datasets.
The most common form of a Databook is an Excel file with multiple spreadsheets.
Databooks can be imported from JSON and YAML;
they can be exported to XLSX, XLS, ODS, JSON, and YAML.


## Usage

Populate fresh data files:

```python
headers = ('first_name', 'last_name')

data = [
    ('John', 'Adams'),
    ('George', 'Washington')
]

data = tablib.Dataset(*data, headers=headers)
```

Intelligently add new rows:

```python
>>> data.append(('Henry', 'Ford'))
```

Intelligently add new columns:

```python
>>> data.append_col((90, 67, 83), header='age')
```

Slice rows:

```python
>>> print(data[:2])
[('John', 'Adams', 90), ('George', 'Washington', 67)]
```

Slice columns by header:

```python
>>> print(data['first_name'])
['John', 'George', 'Henry']
```

Easily delete rows:

```python
>>> del data[1]
```


## Exports

Drumroll please...........

### JSON!

```python
>>> print(data.export('json'))
[
  {
    "last_name": "Adams",
    "age": 90,
    "first_name": "John"
  },
  {
    "last_name": "Ford",
    "age": 83,
    "first_name": "Henry"
  }
]
```

### YAML!

```python
>>> print(data.export('yaml'))
- {age: 90, first_name: John, last_name: Adams}
- {age: 83, first_name: Henry, last_name: Ford}
```

### CSV...

```python
>>> print(data.export('csv'))
first_name,last_name,age
John,Adams,90
Henry,Ford,83
```

### EXCEL!

```python
>>> with open('people.xls', 'wb') as f:
...     f.write(data.export('xls'))
```

### DBF!

```python
>>> with open('people.dbf', 'wb') as f:
...     f.write(data.export('dbf'))
```

### Pandas DataFrame!

```python
>>> print(data.export('df')):
      first_name last_name  age
0       John     Adams   90
1      Henry      Ford   83
```

It's that easy.


## Installation

To install tablib, simply:

```console
$ pip install tablib[pandas]
```

Make sure to check out [Tablib on PyPI](https://pypi.org/project/tablib/)!


## Contribute

Please see the [contributing guide](https://github.com/jazzband/tablib/blob/master/.github/CONTRIBUTING.md).
