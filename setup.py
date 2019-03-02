#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
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
    'tablib.packages.dbfpy',
    'tablib.packages.dbfpy3'
]

install = [
    'odfpy',
    'openpyxl>=2.4.0',
    'backports.csv',
    'xlrd',
    'xlwt',
    'pyyaml',
]


with open('tablib/core.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

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
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    tests_require=['pytest'],
    install_requires=install,
    extras_require={
        'pandas': ['pandas'],
    },
)
