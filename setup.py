#!/usr/bin/env python
# Copyright (c) 2012 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import os
from setuptools import setup, find_packages

def read(*path):
    """
    Read and return content from ``path``
    """
    f = open(
        os.path.join(
            os.path.dirname(__file__),
            *path
        ),
        'r'
    )
    try:
        return f.read().decode('UTF-8')
    finally:
        f.close()

setup(
    name='stormchaser',
    version=read('VERSION.txt').strip().encode('ASCII'),
    description='Track change history for Storm model objects',
    long_description=read('README.rst') + "\n\n" + read("CHANGELOG.rst"),
    author='Oliver Cope',
    license = 'BSD',
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
    package_dir={'': 'src'},
    install_requires=['Storm>=0.19']
)
