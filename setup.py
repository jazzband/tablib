#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from setuptools import find_packages, setup


install = [
    'odfpy',
    'openpyxl>=2.4.0',
    'backports.csv;python_version<"3.0"',
    'markuppy',
    'xlrd',
    'xlwt',
    'pyyaml',
]


setup(
    name='tablib',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Format agnostic tabular data library (XLS, JSON, YAML, CSV)',
    long_description=(open('README.md').read() + '\n\n' +
        open('HISTORY.md').read()),
    long_description_content_type="text/markdown",
    author='Kenneth Reitz',
    author_email='me@kennethreitz.org',
    maintainer='Jazzband',
    maintainer_email='roadies@jazzband.co',
    url='https://tablib.readthedocs.io',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    install_requires=install,
    extras_require={
        'pandas': ['pandas'],
    },
)
