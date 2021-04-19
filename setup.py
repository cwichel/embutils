#!/usr/bin/python
# -*- coding: ascii -*-
"""
Setup script for embutils.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

from embutils.version import SDK_VERSION
from setuptools import setup, find_packages


# Generate setup
setup(
    name='embutils',
    version=SDK_VERSION,
    license="MIT License",
    description='Embedded utilities',
    url='https://github.com/cwichel/embutils',

    author='Christian Wiche',
    author_email='cwichel@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    keywords=[
        'python',
        'embedded',
        'serial',
        'command', 'interface',
        'utilities'
        ],

    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'cryptography',
        'pycryptodome',
        'pycryptodomex',
        'pynput',
        'pyserial',
        'pygetwindow'
        ]
    )
