#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import tablib

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


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

    os.system('pytest test_tablib.py')
    sys.exit()

setup(
    name='tablib',
    version=tablib.__version__,
    description='Format agnostic tabular data library (XLS, JSON, YAML, CSV)',
    long_description=(open('README.rst').read() + '\n\n' +
        open('HISTORY.rst').read()),
    author='Kenneth Reitz',
    author_email='me@kennethreitz.com',
    url='http://python-tablib.org',
    packages=[
        'tablib', 'tablib.formats',
        'tablib.packages',
        'tablib.packages.xlwt',
        'tablib.packages.openpyxl',
        'tablib.packages.openpyxl.shared',
        'tablib.packages.openpyxl.reader',
        'tablib.packages.openpyxl.writer',
        'tablib.packages.yaml',
        'tablib.packages.unicodecsv'
    ],
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
    ),
)
