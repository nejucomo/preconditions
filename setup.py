#! /usr/bin/env python

import sys
from setuptools import setup

if 'upload' in sys.argv:
    if '--sign' not in sys.argv and sys.argv[1:] != ['upload', '--help']:
        raise SystemExit('Refusing to upload unsigned packages.')


PACKAGENAME = 'preconditions'


setup(
    name=PACKAGENAME,
    description='Flexible, concise preconditions.',
    url='https://github.com/nejucomo/{0}'.format(PACKAGENAME),
    license='MIT',
    version='0.1',
    author='Nathan Wilcox',
    author_email='nejucomo@gmail.com',
    py_modules=[PACKAGENAME],
    test_suite='tests',
    )
