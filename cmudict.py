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
	"""
		Parse the entries in the cmudict file.

		The return value is of the form:
			(word, context, phonemes, comment, error)
	"""
	re_linecomment = re.compile(r'^(##|;;;)(.*)$')
	re_entry_cmu = re.compile(r'^([^ ][A-Z0-9\'\.\-\_]*)(\(([1-9])\))? ([A-Z012 ]+)$') # wade/air
	re_entry_new = re.compile(r'^([^ ][a-z0-9\'\.\-\_]*)(\(([1-9])\))?( [A-Z012 ]+)$') # nshmyrev
	re_entry = None
	re_phonemes = re.compile(r' (?=[A-Z][A-Z]?[0-9]?)')
	for line in read_file(filename):
		if line == '':
			yield None, None, None, None, None
			continue

		m = re_linecomment.match(line)
		if m:
			yield None, None, None, m.group(2), None
			continue

		if not re_entry: # detect the dictionary format ...
			if re_entry_new.match(line):
				re_entry = re_entry_new
			else:
				re_entry = re_entry_cmu

		m = re_entry.match(line)
		if not m:
			yield None, None, None, None, 'Unsupported entry: "{0}"'.format(line)
			continue

		phonemes = re_phonemes.split(m.group(4))
		if phonemes[0] == '':
			phonemes = phonemes[1:]
		else:
			yield None, None, None, None, 'Entry needs 2 spaces between word and phoneme: "{0}"'.format(line)

		yield m.group(1), m.group(3), phonemes, None, None
