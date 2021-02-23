"""
Smartbridge provides a uniform interface to multiple smart-device services.
"""

import ast
import os
import re

from setuptools import find_packages
from setuptools import setup

# Cannot use "from smartbridge import get_version" because that would try to
# import the six package which may not be installed yet.
reg = re.compile(r'__version__\s*=\s*(.+)')
with open(os.path.join('smartbridge', '__init__.py')) as f:
    for line in f:
        m = reg.match(line)
        if m:
            version = ast.literal_eval(m.group(1))
            break

REQS_BASE = [
    'deprecation>=2.0.7'
]
REQS_WYZE = [
    'requests>=2.25'
]
REQS_SIMPLE = REQS_BASE + REQS_WYZE
REQS_FULL = REQS_SIMPLE
REQS_DEV = ([
    # 'tox>=2.1.1',
    # 'sphinx>=1.3.1',
    'autopep8>=1.5.5'] + REQS_FULL
)

setup(
    name='smartbridge',
    version=version,
    description='A simple layer of abstraction over multiple smart-device services.',
    long_description=__doc__,
    author='Shaun Tarves',
    author_email='shaun@tarves.net',
    install_requires=[
      REQS_SIMPLE
    ],
    extras_require={
        'wyze': REQS_WYZE,
        'full': REQS_FULL,
        'dev': REQS_DEV
    },
    packages=find_packages(),
    license='The Unlicense',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        "License :: Public Domain",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'],
    test_suite="tests"
)