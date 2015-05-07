#! /usr/bin/env python

from setuptools import setup


PACKAGENAME = 'preconditions'


setup(
    name=PACKAGENAME,
    description='Flexible, concise preconditions.',
    url='https://github.com/nejucomo/{0}'.format(PACKAGENAME),
    license='MIT',
    version='0.1.dev0',
    author='Nathan Wilcox',
    author_email='nejucomo@gmail.com',
    py_modules=[PACKAGENAME],
    test_suite='tests',
    )
