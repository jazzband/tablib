#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Read version from core.py (without importing it)
with open(os.path.join(os.path.dirname(__file__), 'tablib', 'core.py')) as fh:
    for line in fh:
        if line.startswith('__version__'):
            m = re.match(r"^[^=]*=\s'(\d+\.\d+\.\d+)'", line)
            version = m.groups()[0]

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    sys.exit()

if sys.argv[-1] == 'speedups':
    try:
        __import__('pip')
    except ImportError:
        print('Pip required.')
        sys.exit(1)

    os.system('pip install ujson pyyaml')
    sys.exit()

if sys.argv[-1] == 'test':
    try:
        __import__('py')
    except ImportError:
        print('py.test required.')
        sys.exit(1)

    errors = os.system('py.test test_tablib.py')
    sys.exit(bool(errors))

packages = [
    'tablib', 'tablib.formats',
    'tablib.packages',
    'tablib.packages.omnijson',
    'tablib.packages.unicodecsv',
    'tablib.packages.xlwt',
    'tablib.packages.xlrd',
    'tablib.packages.odf',
    'tablib.packages.yaml',
    'tablib.packages.dbfpy',
    'tablib.packages.xlwt3',
    'tablib.packages.xlrd3',
    'tablib.packages.odf3',
    'tablib.packages.yaml3',
    'tablib.packages.dbfpy3'
]

install = [
     'openpyxl',
]


setup(
    name='tablib',
    version=version,
    description='Format agnostic tabular data library (XLS, JSON, YAML, CSV)',
    long_description=(open('README.rst').read() + '\n\n' +
        open('HISTORY.rst').read()),
    author='Kenneth Reitz',
    author_email='me@kennethreitz.org',
    url='http://python-tablib.org',
    packages=packages,
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ),
    install_requires = install,
    tests_require=['pytest'],
)
