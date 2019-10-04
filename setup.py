#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from setuptools import setup


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
    'backports.csv;python_version<"3.0"',
    'markuppy',
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
    long_description=(open('README.md').read() + '\n\n' +
        open('HISTORY.md').read()),
    long_description_content_type="text/markdown",
    author='Kenneth Reitz',
    author_email='me@kennethreitz.org',
    url='https://tablib.readthedocs.io',
    packages=packages,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    tests_require=['pytest'],
    install_requires=install,
    extras_require={
        'pandas': ['pandas'],
    },
)
