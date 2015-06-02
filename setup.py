#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


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

    errors = os.system('py.test test_tablib.py')
    sys.exit(bool(errors))

packages = [
    'tablib', 'tablib.formats',
    'tablib.packages',
]

install = [
    'xlrd',      # xlrd==0.9.3
    'openpyxl',  # openpyxl==2.2.3
    'pyyaml',    # pyyaml==3.11
    'xlwt',      # xlwt==1.0.0
    #'omnijson',  # omnijson==0.1.2
]

if sys.version_info[0] == 2:
    packages.extend([
        'tablib.packages.odf',
        'tablib.packages.dbfpy'
    ])
    # unicodecsv defaults to stdlib csv library in python 3,
    # so only install it in python 2
    install.append('unicodecsv')  # unicodecsv==0.13.0
else:
    packages.extend([
        'tablib.packages.odf3',
        'tablib.packages.dbfpy3'
    ])


setup(
    name='tablib',
    version='0.10.0',
    description='Format agnostic tabular data library (XLS, JSON, YAML, CSV)',
    long_description=(open('README.rst').read() + '\n\n' +
        open('HISTORY.rst').read()),
    author='Kenneth Reitz',
    author_email='me@kennethreitz.org',
    url='http://python-tablib.org',
    packages=packages,
    license='MIT',
    install_requires = install,
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
    tests_require=['pytest'],
)
