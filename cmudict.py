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

from __future__ import print_function

import os
import sys
import re

VOWEL = 1
CONSONANT = 2

phoneme_table = [
	{'cmudict': 'AA', 'type': VOWEL,     'example': ('odd',     'AA D')},
	{'cmudict': 'AE', 'type': VOWEL,     'example': ('at',      'AE T')},
	{'cmudict': 'AH', 'type': VOWEL,     'example': ('hut',     'HH AH T')},
	{'cmudict': 'AO', 'type': VOWEL,     'example': ('ought',   'AO T')},
	{'cmudict': 'AW', 'type': VOWEL,     'example': ('cow',     'K AW')},
	{'cmudict': 'AY', 'type': VOWEL,     'example': ('hide',    'HH AY D')},
	{'cmudict': 'B',  'type': CONSONANT, 'example': ('be',      'B IY')},
	{'cmudict': 'CH', 'type': CONSONANT, 'example': ('cheese',  'CH IY Z')},
	{'cmudict': 'D',  'type': CONSONANT, 'example': ('dee',     'D IY')},
	{'cmudict': 'DH', 'type': CONSONANT, 'example': ('thee',    'DH IY')},
	{'cmudict': 'EH', 'type': VOWEL,     'example': ('Ed',      'EH D')},
	{'cmudict': 'ER', 'type': VOWEL,     'example': ('hurt',    'HH ER T')},
	{'cmudict': 'EY', 'type': VOWEL,     'example': ('ate',     'EY T')},
	{'cmudict': 'F',  'type': CONSONANT, 'example': ('fee',     'F IY')},
	{'cmudict': 'G',  'type': CONSONANT, 'example': ('green',   'G R IY N')},
	{'cmudict': 'HH', 'type': CONSONANT, 'example': ('he',      'HH IY')},
	{'cmudict': 'IH', 'type': VOWEL,     'example': ('it',      'IH T')},
	{'cmudict': 'IY', 'type': VOWEL,     'example': ('eat',     'IY T')},
	{'cmudict': 'JH', 'type': CONSONANT, 'example': ('gee',     'JH IY')},
	{'cmudict': 'K',  'type': CONSONANT, 'example': ('key',     'K IY')},
	{'cmudict': 'L',  'type': CONSONANT, 'example': ('lee',     'L IY')},
	{'cmudict': 'M',  'type': CONSONANT, 'example': ('me',      'M IY')},
	{'cmudict': 'N',  'type': CONSONANT, 'example': ('knee',    'N IY')},
	{'cmudict': 'NG', 'type': CONSONANT, 'example': ('ping',    'P IH NG')},
	{'cmudict': 'OW', 'type': VOWEL,     'example': ('oat',     'OW T')},
	{'cmudict': 'OY', 'type': VOWEL,     'example': ('toy',     'T OY')},
	{'cmudict': 'P',  'type': CONSONANT, 'example': ('pee',     'P IY')},
	{'cmudict': 'R',  'type': CONSONANT, 'example': ('read',    'R IY D')},
	{'cmudict': 'S',  'type': CONSONANT, 'example': ('sea',     'S IY')},
	{'cmudict': 'SH', 'type': CONSONANT, 'example': ('she',     'SH IY')},
	{'cmudict': 'T',  'type': CONSONANT, 'example': ('tea',     'T IY')},
	{'cmudict': 'TH', 'type': CONSONANT, 'example': ('theta',   'TH EY T AH')},
	{'cmudict': 'UH', 'type': VOWEL,     'example': ('hood',    'HH UH D')},
	{'cmudict': 'UW', 'type': VOWEL,     'example': ('two',     'T UW')},
	{'cmudict': 'V',  'type': CONSONANT, 'example': ('vee',     'V IY')},
	{'cmudict': 'W',  'type': CONSONANT, 'example': ('we',      'W IY')},
	{'cmudict': 'Y',  'type': CONSONANT, 'example': ('yield',   'Y IY L D')},
	{'cmudict': 'Z',  'type': CONSONANT, 'example': ('zee',     'Z IY')},
	{'cmudict': 'ZH', 'type': CONSONANT, 'example': ('seizure', 'S IY ZH ER')},
]

dict_formats = { # {0} = word ; {1} = context ; {2} = phonemes ; {3} = comment
	'cmudict-weide': {
		'comment': '##{3}',
		'entry': '{0}  {2}',
		'entry-comment': '{0}  {2} #{3}',
		'entry-context': '{0}({1})  {2}',
		'entry-context-comment': '{0}({1})  {2} #{3}',
		'phonemes': lambda phonemes: ' '.join(phonemes),
		'word': lambda word: word.upper(),
	},
	'cmudict': {
		'comment': ';;;{3}',
		'entry': '{0}  {2}',
		'entry-comment': '{0}  {2} #{3}',
		'entry-context': '{0}({1})  {2}',
		'entry-context-comment': '{0}({1})  {2} #{3}',
		'phonemes': lambda phonemes: ' '.join(phonemes),
		'word': lambda word: word.upper(),
	},
	'cmudict-new': {
		'comment': ';;;{3}',
		'entry': '{0} {2}',
		'entry-context': '{0}({1}) {2}',
		'entry-comment': '{0} {2} #{3}',
		'entry-context-comment': '{0}({1}) {2} #{3}',
		'phonemes': lambda phonemes: ' '.join(phonemes),
		'word': lambda word: word.lower(),
	},
}

parser_warnings = {
	'context-values': 'check context values are numbers',
	'context-ordering': 'check context values are ordered sequentially',
	'duplicate-pronunciations': 'check for duplicated pronunciations for an entry',
	'entry-spacing': 'check spacing between word and pronunciation',
	'invalid-phonemes': 'check for invalid phonemes',
	'missing-stress': 'check for missing stress markers',
	'phoneme-spacing': 'check for a single space between phonemes',
	'trailing-whitespace': 'check for trailing whitespaces',
	'word-casing': 'check for consistent word casing',
}

default_warnings = [
	'context-values',
	'context-ordering',
	'entry-spacing',
	'invalid-phonemes',
	'phoneme-spacing',
	'word-casing'
]

# dict() is too slow for indexing cmudict entries, so use a simple trie
# data structure instead ...
class Trie:
	def __init__(self):
		self.root = {}

	def lookup(self, key):
		current = self.root
		for letter in key:
			if letter in current:
				current = current[letter]
			else:
				return False, None
		if None in current:
			return True, current[None]
		return False, None

	def __contains__(self, key):
		valid, _ = self.lookup(key)
		return valid

	def __getitem__(self, key):
		valid, item = self.lookup(key)
		if not valid:
			raise KeyError('Item not in Trie')
		return item

	def __setitem__(self, key, value):
		current = self.root
		for letter in key:
			current = current.setdefault(letter, {})
		current[None] = value

def sort(entries, mode):
	if mode is None:
		for entry in entries:
			yield entry
	elif mode in ['weide', 'air']:
		ordered = []
		for word, context, phonemes, comment, error in entries:
			if not word:
				yield (word, context, phonemes, comment, error)
				continue
			if mode == 'weide':
				if context:
					key = '{0}({1})'.format(word, context)
				else:
					key = word
			elif mode == 'air':
				if context:
					key = '{0}!{1}'.format(word, context)
				else:
					key = word
			ordered.append((key, (word, context, phonemes, comment, error)))
		for key, entry in sorted(ordered):
			yield entry
	else:
		raise ValueError('unsupported sort mode: {0}'.format(mode))

def format(dict_format, entries):
	fmt = dict_formats[dict_format]
	for word, context, phonemes, comment, error in entries:
		if error:
			print(error, file=sys.stderr)
			continue
		components = []
		if word:
			components.append('entry')
			word = fmt['word'](word)
		if context:
			components.append('context')
		if comment != None:
			components.append('comment')
		if phonemes:
			phonemes = fmt['phonemes'](phonemes)
		if len(components) == 0:
			print()
		else:
			print(fmt['-'.join(components)].format(word, context, phonemes, comment))

def read_file(filename):
	with open(filename) as f:
		for line in f:
			yield line.replace('\n', '')

def parse(filename, warnings=[], order_from=0):
	"""
		Parse the entries in the cmudict file.

		The return value is of the form:
			(word, context, phonemes, comment, error)
	"""
	GROUP_WORD     = 1
	GROUP_CONTEXT  = 3 # 2 = with context markers ~ ({3})
	GROUP_SPACING  = 4
	GROUP_PHONEMES = 5
	GROUP_COMMENT  = 7 # 6 = with comment marker ~ #{7}

	checks = default_warnings
	for warning in warnings:
		if warning == 'all':
			checks = parser_warnings.keys()
		elif warning == 'none':
			checks = []
		elif warning.startswith('no-'):
			if warning[3:] in parser_warnings.keys():
				if warning[3:] in checks:
					checks.remove(warning[3:])
			else:
				raise ValueError('Invalid warning: {0}'.format(warning))
		elif warning in parser_warnings.keys():
			if warning not in checks:
				checks.append(warning)
		else:
			raise ValueError('Invalid warning: {0}'.format(warning))

	re_linecomment = re.compile(r'^(##|;;;)(.*)$')
	re_entry = re.compile(r'^([^ a-zA-Z]?[a-zA-Z0-9\'\.\-\_]*)(\(([^\)]*)\))?([ \t]+)([^#]+)( #(.*))?[ \t]*$')
	re_word_cmu = re.compile(r'^[^ a-zA-Z]?[A-Z0-9\'\.\-\_]*$') # weide/air
	re_word_new = re.compile(r'^[^ a-zA-Z]?[a-z0-9\'\.\-\_]*$') # nshmyrev
	re_word = None
	re_phonemes = re.compile(r' (?=[A-Z][A-Z]?[0-9]?)')
	re_phoneme_start = re.compile(r'^ [A-Z]')

	entries = Trie()
	valid_phonemes = set()
	missing_stress_marks = set()
	for line in read_file(filename):
		if line == '':
			yield None, None, None, None, None
			continue

		m = re_linecomment.match(line)
		if m:
			yield None, None, None, m.group(2), None
			continue

		m = re_entry.match(line)
		if not m:
			yield None, None, None, None, 'Unsupported entry: "{0}"'.format(line)
			continue

		word = m.group(GROUP_WORD)
		if not re_word: # detect the dictionary format ...
			if re_word_cmu.match(word):
				re_word = re_word_cmu
				spacing = '  '
			else:
				re_word = re_word_new
				spacing = ' '
			for p in phoneme_table:
				if p['type'] == VOWEL:
					missing_stress_marks.add(p['cmudict'])
					valid_phonemes.add('{0}0'.format(p['cmudict']))
					valid_phonemes.add('{0}1'.format(p['cmudict']))
					valid_phonemes.add('{0}2'.format(p['cmudict']))
				else:
					valid_phonemes.add(p['cmudict'])

		if not re_word.match(word) and 'word-casing' in checks:
			yield None, None, None, None, 'Incorrect word casing in entry: "{0}"'.format(line)

		try:
			context = m.group(GROUP_CONTEXT)
			if context is not None:
				context = int(context)
		except ValueError:
			if 'context-values' in checks:
				yield None, None, None, None, 'Invalid context format "{0}" in entry: "{1}"'.format(m.group(GROUP_CONTEXT), line)
			context = m.group(GROUP_CONTEXT)

		if m.group(GROUP_SPACING) != spacing and 'entry-spacing' in checks:
			yield None, None, None, None, 'Entry needs {0} spaces between word and phoneme: "{1}"'.format(len(spacing), line)

		phonemes = m.group(GROUP_PHONEMES)
		if phonemes.endswith(' ') and 'trailing-whitespace' in checks:
			yield None, None, None, None, 'Trailing whitespace in entry: "{0}"'.format(line)

		phonemes = re_phonemes.split(phonemes.strip())
		for phoneme in phonemes:
			if ' ' in phoneme or '\t' in phoneme:
				phoneme = phoneme.strip()
				if 'phoneme-spacing' in checks:
					yield None, None, None, None, 'Incorrect whitespace after phoneme in entry: "{1}"'.format(phoneme, line)
			if phoneme in missing_stress_marks:
				if 'missing-stress' in checks:
					yield None, None, None, None, 'Vowel phoneme "{0}" missing stress marker in entry: "{1}"'.format(phoneme, line)
			elif not phoneme in valid_phonemes:
				if 'invalid-phonemes' in checks:
					yield None, None, None, None, 'Invalid phoneme "{0}" in entry: "{1}"'.format(phoneme, line)

		key = word.upper()
		position = order_from if context is None else context

		if isinstance(position, int):
			pronunciation = ' '.join(phonemes)
			if key in entries:
				expect_position, pronunciations = entries[key]
			else:
				expect_position = order_from
				pronunciations = []
			if position != expect_position and 'context-ordering' in checks:
				yield None, None, None, None, 'Incorrect context ordering "{0}" (expected: "{1}") in entry: "{2}"'.format(position, expect_position, line)
			expect_position = expect_position + 1
			if pronunciation in pronunciations:
				if 'duplicate-pronunciations' in checks:
					yield None, None, None, None, 'Existing pronunciation in entry: "{2}"'.format(position, expect_position, line)
			else:
				pronunciations.append(pronunciation)
			entries[key] = (expect_position, pronunciations)

		comment = m.group(GROUP_COMMENT) or None
		yield word, context, phonemes, comment, None
