#!/usr/bin/python
# coding=utf-8
#
# cmudict-tools setup script
#
# Copyright (C) 2015 Reece H. Dunn
#
# This file is part of cmudict-tools.
#
# cmudict-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cmudict-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cmudict-tools.  If not, see <http://www.gnu.org/licenses/>.

import codecs

from setuptools import setup

def read_file(filename, encoding='utf-8'):
	with codecs.open(filename, 'r', encoding) as f:
		return f.read()

setup(name='cmudict-tools',
      version='1.0',
      description='Tools for working with cmudict and festlex pronunciation dictionaries.',
      long_description=read_file('README.rst'),
      url='https://github.com/rhdunn/cmudict-tools',
      author='Reece H. Dunn',
      author_email='msclrhd@gmail.com',
      license='GPLv3+',
      classifiers=[ # See: https://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Linguistic',
      ],
      keywords='cmudict festlex pronunciation dictionary parse sort format filter',
      packages=['cmudicttools'],
      package_data = {
          'cmudicttools': ['accents/*.csv'],
      },
      scripts=['cmudict-tools'])
