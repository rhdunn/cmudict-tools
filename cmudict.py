#!/usr/bin/python
#
# Tool for processing the CMU Pronunciation Dictionary file formats.
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

import os
import sys
import re

def read_file(filename):
	with open(filename) as f:
		for line in f:
			yield line.replace('\n', '')

def parse_cmudict(filename):
	re_entry = re.compile(r'^([A-Z0-9\'\.\-]+)(\(([1-9])\))?  ([A-Z012 ]+)$')
	for line in read_file(filename):
		m = re_entry.match(line)
		if m:
			yield m.group(1), m.group(3), m.group(4)
			continue
		raise Exception('Unsupported entry: "{0}"'.format(line))
