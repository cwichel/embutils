#!/usr/bin/env python
from embutils import VERSION
from setuptools import setup, find_packages

# Get requirement list
DEPENDENCIES = []
DEPENDENCIES_TEMP = [i.strip() for i in open(file='requirements.txt', mode='r').readlines()]
for req in DEPENDENCIES_TEMP:
    req = req.replace('==', '>=') if ('==' in req) else req
    DEPENDENCIES.append(req)

# Generate setup
setup(
    name='embutils',
    version=VERSION,
    description='Embedded utilities',
    url='https://github.com/cwichel/embutils',

    author='Christian Wiche',
    author_email='cwichel@gmail.com',
    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        ],
    keywords='python embedded serial command interface utilities',

    packages=find_packages(),

    python_requires='>=3.6',
    install_requires=DEPENDENCIES
    )
