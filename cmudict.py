#!/usr/bin/python
# coding=utf-8
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
import json
import codecs

import metadata

root = os.path.dirname(os.path.realpath(__file__))

if sys.version_info[0] == 2:
	ustr = unicode

	def printf(fmt, encoding, *args):
		output = unicode(fmt).format(*args)
		sys.stdout.write(output.encode(encoding))
else:
	ustr = str

	def printf(fmt, encoding, *args):
		output = fmt.format(*args)
		sys.stdout.buffer.write(output.encode(encoding))

def read_phonetable(filename):
	columns = None
	for data in metadata.parse_csv(filename):
		data['Phone Sets'] = data['Phone Sets'].split(';')
		yield data

def festlex_context(context):
	if not context in ['dt', 'j', 'n', 'nil', 'v', 'v_p', 'vl', 'y']:
		raise ValueError('Unknown festlex context value: {0}'.format(context))
	return context

class SetValidator:
	def __init__(self, values):
		self.values = values

	def __call__(self, value):
		return value in self.values

class TypeValidator:
	_types = { 's': str, 'i': int, 'f': float }

	def __init__(self, value_type):
		self.value_type = self._types[value_type]

	def __call__(self, value):
		try:
			self.value_type(value)
			return True
		except ValueError:
			return False

class IpaPhonemeSet:
	def __init__(self, accent):
		self.to_ipa = {}
		self.accent = accent

	def add(self, data):
		if not data[self.accent]:
			return # not supported in this accent
		arpabet = data['Arpabet']
		ipa = data[self.accent]
		types = data['Type'].split(';')
		if 'vowel' in types:
			self.to_ipa[arpabet] = ipa # missing stress
			self.to_ipa['{0}0'.format(arpabet)] = ipa
			self.to_ipa['{0}1'.format(arpabet)] = u'ˈ{0}'.format(ipa)
			self.to_ipa['{0}2'.format(arpabet)] = u'ˌ{0}'.format(ipa)
		elif 'schwa' in types:
			self.to_ipa[arpabet] = ipa # missing stress
			self.to_ipa['{0}0'.format(arpabet)] = ipa
		else:
			self.to_ipa[arpabet] = ipa

	def parse(self, phonemes, checks):
		raise Exception('parse is not currently supported for IPA phonemes')

	def to_local_phonemes(self, phonemes):
		for phoneme in phonemes:
			if phoneme in self.to_ipa.keys():
				yield self.to_ipa[phoneme]

	def format(self, phonemes):
		return ''.join(self.to_local_phonemes(phonemes))

class ArpabetPhonemeSet:
	def __init__(self, capitalization):
		self.re_phonemes = re.compile(r' (?=[^ ])')
		if capitalization == 'upper':
			self.conversion = ustr.upper
			self.parse_phoneme = ustr # already upper case
		elif capitalization == 'lower':
			self.conversion = ustr.lower
			self.parse_phoneme = ustr.upper
		else:
			raise ValueError('Unsupported capitalization value: {0}'.format(capitalization))
		self.to_arpabet = {}
		self.from_arpabet = {}
		self.missing_stress_marks = set()

	def add(self, data):
		phoneme = self.conversion(data['Arpabet'])
		normalized = self.conversion(data['Normalized'] if data['Normalized'] else phoneme)
		types = data['Type'].split(';')
		if 'vowel' in types:
			self.missing_stress_marks.add(phoneme)
			self.to_arpabet[phoneme] = normalized
			self.to_arpabet['{0}0'.format(phoneme)] = u'{0}0'.format(normalized)
			self.to_arpabet['{0}1'.format(phoneme)] = u'{0}1'.format(normalized)
			self.to_arpabet['{0}2'.format(phoneme)] = u'{0}2'.format(normalized)
			self.from_arpabet[normalized] = phoneme
			self.from_arpabet['{0}0'.format(normalized)] = u'{0}0'.format(phoneme)
			self.from_arpabet['{0}1'.format(normalized)] = u'{0}1'.format(phoneme)
			self.from_arpabet['{0}2'.format(normalized)] = u'{0}2'.format(phoneme)
		elif 'schwa' in types:
			self.to_arpabet[phoneme] = normalized
			self.to_arpabet['{0}0'.format(phoneme)] = u'{0}0'.format(normalized)
			self.from_arpabet[normalized] = phoneme
			self.from_arpabet['{0}0'.format(normalized)] = u'{0}0'.format(phoneme)
		else:
			self.to_arpabet[phoneme] = normalized
			self.from_arpabet[normalized] = phoneme

	def parse(self, phonemes, checks):
		for phoneme in self.re_phonemes.split(phonemes.strip()):
			if ' ' in phoneme or '\t' in phoneme:
				phoneme = phoneme.strip()
				if 'phoneme-spacing' in checks:
					yield None, 'Incorrect whitespace after phoneme "{0}"'.format(phoneme)

			if phoneme in self.missing_stress_marks:
				if 'missing-stress' in checks:
					yield None, 'Vowel phoneme "{0}" missing stress marker'.format(phoneme)
			elif not phoneme in self.to_arpabet.keys():
				newphoneme = self.conversion(phoneme)
				if 'invalid-phonemes' in checks:
					if newphoneme in self.missing_stress_marks:
						if 'missing-stress' in checks:
							yield None, 'Vowel phoneme "{0}" missing stress marker'.format(phoneme)
					elif not newphoneme in self.to_arpabet.keys():
						yield None, 'Invalid phoneme "{0}"'.format(phoneme)
					else:
						yield None, 'Incorrect phoneme casing "{0}"'.format(phoneme)
				yield newphoneme, None
				continue

			yield self.to_arpabet[phoneme], None

	def to_local_phonemes(self, phonemes):
		for phoneme in phonemes:
			phoneme = self.conversion(phoneme)
			if phoneme in self.from_arpabet.keys():
				yield self.from_arpabet[phoneme]
			else:
				yield phoneme

	def format(self, phonemes):
		return ' '.join(self.to_local_phonemes(phonemes))

phonesets = {
	'arpabet':  lambda: ArpabetPhonemeSet('upper'),
	'cepstral': lambda: ArpabetPhonemeSet('lower'),
	'cmu':      lambda: ArpabetPhonemeSet('upper'),
	'festvox':  lambda: ArpabetPhonemeSet('lower'),
	'ipa':      lambda: IpaPhonemeSet('IPA'),
	'timit':    lambda: ArpabetPhonemeSet('lower'),
}

def load_phonemes(accent, phoneset):
	phones = phonesets[phoneset]()
	if not accent.endswith('.csv'):
		accent = os.path.join(root, 'accents', '{0}.csv'.format(accent))
	for p in read_phonetable(accent):
		if phoneset in p['Phone Sets']:
			phones.add(p)
	return phones

dict_formats = { # {0} = word ; {1} = context ; {2} = phonemes ; {3} = comment
	'cmudict-weide': {
		'accent': 'en-US',
		'phoneset': 'cmu',
		# formatting:
		'comment': '##{3}\n',
		'entry': '{0}  {2}\n',
		'entry-comment': '{0}  {2} #{3}\n',
		'entry-context': '{0}({1})  {2}\n',
		'entry-context-comment': '{0}({1})  {2} #{3}\n',
		'word': lambda word: word.upper(),
		# parsing:
		'word-validation': r'^[^ a-zA-Z]?[A-Z0-9\'\.\-\_\x80-\xFF]*$',
		'context-parser': int,
	},
	'cmudict': {
		'accent': 'en-US',
		'phoneset': 'cmu',
		# formatting:
		'comment': ';;;{3}\n',
		'entry': '{0}  {2}\n',
		'entry-comment': '{0}  {2} #{3}\n',
		'entry-context': '{0}({1})  {2}\n',
		'entry-context-comment': '{0}({1})  {2} #{3}\n',
		'word': lambda word: word.upper(),
		# parsing:
		'word-validation': r'^[^ a-zA-Z]?[A-Z0-9\'\.\-\_\x80-\xFF]*$',
		'context-parser': int,
	},
	'cmudict-new': {
		'accent': 'en-US',
		'phoneset': 'cmu',
		# formatting:
		'comment': ';;;{3}\n',
		'entry': '{0} {2}\n',
		'entry-context': '{0}({1}) {2}\n',
		'entry-comment': '{0} {2} #{3}\n',
		'entry-context-comment': '{0}({1}) {2} #{3}\n',
		'word': lambda word: word.lower(),
		# parsing:
		'word-validation': r'^[^ a-zA-Z]?[a-z0-9\'\.\-\_\x80-\xFF]*$',
		'context-parser': int,
	},
	'festlex': {
		'accent': 'en-US',
		'phoneset': 'festvox',
		# formatting:
		'comment': ';;{3}\n',
		'entry': '("{0}" nil ({2}))\n',
		'entry-context': '("{0}" {1} ({2}))\n',
		'entry-comment': '("{0}" nil ({2})) ;{3}\n',
		'entry-context-comment': '("{0}" {1} ({2})) ;{3}\n',
		'word': lambda word: word.lower(),
		# parsing:
		'word-validation': r'^[^ a-zA-Z]?[a-z0-9\'\.\-\_\x80-\xFF]*$',
		'context-parser': festlex_context,
	},
}

parser_warnings = {
	'context-values': 'check context values are numbers',
	'context-ordering': 'check context values are ordered sequentially',
	'duplicate-entries': 'check for matching entries (word, context, pronunciation)',
	'duplicate-pronunciations': 'check for duplicated pronunciations for an entry',
	'entry-spacing': 'check spacing between word and pronunciation',
	'invalid-phonemes': 'check for invalid phonemes',
	'missing-stress': 'check for missing stress markers',
	'phoneme-spacing': 'check for a single space between phonemes',
	'trailing-whitespace': 'check for trailing whitespaces',
	'unsorted': 'check if a word is not sorted correctly',
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
		for word, context, phonemes, comment, metadata, error in entries:
			if not word:
				yield (word, context, phonemes, comment, metadata, error)
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
			ordered.append((key, (word, context, phonemes, comment, metadata, error)))
		for key, entry in sorted(ordered):
			yield entry
	else:
		raise ValueError('unsupported sort mode: {0}'.format(mode))

def format_text(dict_format, entries, accent=None, phoneset=None, encoding='windows-1252'):
	fmt = dict_formats[dict_format]
	if not accent:
		accent = fmt['accent']
	if not phoneset:
		phoneset = fmt['phoneset']
	if phoneset == 'ipa':
		encoding = 'utf-8'
	phonemeset = load_phonemes(accent, phoneset)
	for word, context, phonemes, comment, metadata, error in entries:
		if error:
			print(error, file=sys.stderr)
			continue
		components = []
		if word:
			components.append('entry')
			word = fmt['word'](word)
		if context:
			components.append('context')
		if comment != None or metadata != None:
			if metadata != None:
				meta = []
				for key, values in sorted(metadata.items()):
					meta.extend(['{0}={1}'.format(key, value) for value in values])
				if comment:
					comment = '@@ {0} @@{1}'.format(' '.join(meta), comment)
				else:
					comment = '@@ {0} @@'.format(' '.join(meta))
			components.append('comment')
		if phonemes:
			phonemes = phonemeset.format(phonemes)
		if len(components) == 0:
			print()
		else:
			printf(fmt['-'.join(components)], encoding, word, context, phonemes, comment)

def format_json(dict_format, entries, accent=None, phoneset=None, encoding='windows-1252'):
	fields = ['word', 'context', 'pronunciation', 'comment', 'metadata', 'error-message']
	need_comma = False
	printf('[\n', encoding)
	for entry in entries:
		data = dict([(k, v) for k, v in zip(fields, entry) if v != None])
		if need_comma:
			printf(',\n', encoding)
		printf('{0}', encoding, json.dumps(data, sort_keys=True))
		need_comma = True
	if need_comma:
		printf('\n]\n', encoding)
	else:
		printf(']\n', encoding)

def format(dict_format, entries, accent=None, phoneset=None, encoding='windows-1252'):
	if dict_format in ['json']:
		format_json(dict_format, entries, accent, phoneset, encoding)
	else:
		format_text(dict_format, entries, accent, phoneset, encoding)

def read_file(filename, encoding='windows-1252'):
	with codecs.open(filename, encoding=encoding) as f:
		for line in f:
			yield line.replace('\r', '').replace('\n', '')

class InvalidWarning(ValueError):
	def __init__(self, message):
		ValueError.__init__(self, message)

def warnings_to_checks(warnings):
	checks = default_warnings
	for warning in warnings:
		if warning == 'all':
			checks = list(parser_warnings.keys())
		elif warning == 'none':
			checks = []
		elif warning.startswith('no-'):
			if warning[3:] in parser_warnings.keys():
				if warning[3:] in checks:
					checks.remove(warning[3:])
			else:
				raise InvalidWarning('Invalid warning: {0}'.format(warning))
		elif warning in parser_warnings.keys():
			if warning not in checks:
				checks.append(warning)
		else:
			raise InvalidWarning('Invalid warning: {0}'.format(warning))
	return checks

def parse_comment_string(comment, values=None):
	metadata = None
	errors = []
	re_key   = re.compile(r'^[a-zA-Z0-9_\-]+$')
	re_value = re.compile(r'^[^\x00-\x20\x7F-\xFF"]+$')
	if comment.startswith('@@'):
		_, metastring, comment = comment.split('@@')
		metadata = {}
		for key, value in [x.split('=') for x in metastring.strip().split()]:
			if values is not None:
				if not key in values.keys():
					errors.append('Invalid metadata key "{0}"'.format(key))
				elif not values[key](value):
					errors.append('Invalid metadata value "{0}"'.format(value))
			else:
				if not re_key.match(key):
					errors.append('Invalid metadata key "{0}"'.format(key))
				if not re_value.match(value):
					errors.append('Invalid metadata value "{0}"'.format(value))

			if key in metadata.keys():
				metadata[key].append(value)
			else:
				metadata[key] = [value]
	return comment, metadata, errors

def parse_festlex(filename, checks, order_from, encoding):
	"""
		Parse the entries in a festlex formatted dictionary (e.g. festlex-cmu).

		The return value is of the form:
			(line, format, word, context, phonemes, comment, error)
	"""

	re_linecomment = re.compile(r'^;;(.*)$')
	re_entry = re.compile(r'^\("([^"]+)" ([a-zA-Z0-9_]+) \(([^\)]+)\)[ \t]*\)[ \t]*(;(.*))?[ \t]*$')
	format = 'festlex'
	for line in read_file(filename, encoding=encoding):
		if line == '':
			yield line, format, None, None, None, None, None, None
			continue

		m = re_linecomment.match(line)
		if m:
			comment, meta, errors = parse_comment_string(m.group(1))
			for message in errors:
				yield line, format, None, None, None, None, None, '{0} in entry: "{1}"'.format(message, line)
			yield line, format, None, None, None, comment, meta, None
			continue

		m = re_entry.match(line)
		if not m:
			yield line, format, None, None, None, None, None, 'Unsupported entry: "{0}"'.format(line)
			continue

		word = m.group(1)
		context = m.group(2)
		phonemes = m.group(3)
		comment = m.group(5)
		meta = None
		if comment:
			comment, meta, errors = parse_comment_string(comment)
			for message in errors:
				yield line, format, None, None, None, None, None, '{0} in entry: "{1}"'.format(message, line)

		if context == 'nil':
			context = None

		yield line, format, word, context, phonemes, comment, meta, None

def parse_cmudict(filename, checks, order_from, encoding):
	"""
		Parse the entries in the cmudict file.

		The return value is of the form:
			(line, format, word, context, phonemes, comment, error)
	"""
	re_linecomment_weide = re.compile(r'^##(.*)$')
	re_linecomment_air   = re.compile(r'^;;;(.*)$')
	re_entry = re.compile(r'^([^ a-zA-Z\x80-\xFF]?[a-zA-Z0-9\'\.\-\_\x80-\xFF]*)(\(([^\)]*)\))?([ \t]+)([^#]+)( #(.*))?[ \t]*$')
	format = None
	entry_metadata = {}
	for line in read_file(filename, encoding=encoding):
		if line == '':
			yield line, format, None, None, None, None, None, None
			continue

		comment = None
		m = re_linecomment_weide.match(line)
		if m:
			comment, meta, errors = parse_comment_string(m.group(1))
			comment_format = 'cmudict-weide'

		m = re_linecomment_air.match(line)
		if m:
			comment, meta, errors = parse_comment_string(m.group(1))
			comment_format = 'cmudict-air'

		if comment is not None:
			for message in errors:
				yield line, format, None, None, None, None, None, '{0} in entry: "{1}"'.format(message, line)
			if meta:
				if 'format' in meta.keys():
					format = meta['format'][0]
					if format == 'cmudict-new':
						spacing = ' '
					else:
						spacing = '  '
				if 'metadata' in meta.keys():
					if not entry_metadata:
						entry_metadata = {}
					entry = meta['metadata'][0]
					if entry.startswith('@'):
						t, key = entry[1:].split(':')
						entry_metadata[key] = TypeValidator(t)
					else:
						path = os.path.join(os.path.dirname(filename), entry)
						for key, value in metadata.parse(path).items():
							entry_metadata[key] = SetValidator(value)
			if not format: # detect the dictionary format ...
				format = comment_format
				if format == 'cmudict-new':
					spacing = ' '
				else:
					spacing = '  '
			if format != 'cmudict-weide' and comment_format == 'cmudict-weide':
				yield line, format, None, None, None, None, None, u'Old-style comment: "{0}"'.format(line)
			elif format == 'cmudict-weide' and comment_format == 'cmudict-air':
				yield line, format, None, None, None, None, None, u'New-style comment: "{0}"'.format(line)
			yield line, format, None, None, None, comment, meta, None
			continue

		m = re_entry.match(line)
		if not m:
			yield line, format, None, None, None, None, None, u'Unsupported entry: "{0}"'.format(line)
			continue

		word = m.group(1)
		context = m.group(3) # 2 = with context markers: `(...)`
		word_phoneme_space = m.group(4)
		phonemes = m.group(5)
		comment = m.group(7) or None # 6 = with comment marker: `#...`
		meta = None
		if comment:
			comment, meta, errors = parse_comment_string(comment, values=entry_metadata)
			for message in errors:
				yield line, format, None, None, None, None, None, '{0} in entry: "{1}"'.format(message, line)

		if not format or format == 'cmudict-air': # detect the dictionary format ...
			cmudict_fmt = re.compile(dict_formats['cmudict']['word-validation'])
			if cmudict_fmt.match(word):
				format = 'cmudict'
				spacing = '  '
			else:
				format = 'cmudict-new'
				spacing = ' '

		if word_phoneme_space != spacing and 'entry-spacing' in checks:
			yield line, format, None, None, None, None, None, u'Entry needs {0} spaces between word and phoneme: "{1}"'.format(len(spacing), line)

		if phonemes.endswith(' ') and 'trailing-whitespace' in checks:
			yield line, format, None, None, None, None, None, u'Trailing whitespace in entry: "{0}"'.format(line)

		yield line, format, word, context, phonemes, comment, meta, None

def parse(filename, warnings=[], order_from=0, accent=None, phoneset=None, encoding='windows-1252'):
	checks = warnings_to_checks(warnings)
	previous_word = None
	re_word = None
	context_parser = None
	phonemeset = None
	entries = Trie()
	lines = Trie()
	fmt = None

	if filename.endswith('.scm'):
		dict_parser = parse_festlex
	else:
		dict_parser = parse_cmudict

	for line, format, word, context, phonemes, comment, meta, error in dict_parser(filename, checks, order_from, encoding):
		if error:
			yield None, None, None, None, None, error
			continue

		if not word: # line comment or blank line
			yield None, None, None, comment, meta, None
			continue

		if not fmt:
			fmt = dict_formats[format]
			if not accent:
				accent = fmt['accent']
			if not phoneset:
				phoneset = fmt['phoneset']
			phonemeset = load_phonemes(accent, phoneset)
			context_parser = fmt['context-parser']

		# word validation checks

		if fmt['word'](word) != word and 'word-casing' in checks:
			yield None, None, None, None, None, u'Incorrect word casing in entry: "{0}"'.format(line)

		if previous_word and word < previous_word and 'unsorted' in checks:
			yield None, None, None, None, None, u'Incorrect word ordering ("{0}" < "{1}") for entry: "{2}"'.format(word, previous_word, line)

		# context parsing and validation checks

		try:
			if context is not None:
				context = context_parser(context)
		except ValueError:
			if 'context-values' in checks:
				yield None, None, None, None, None, u'Invalid context format "{0}" in entry: "{1}"'.format(context, line)

		# phoneme validation checks

		arpabet_phonemes = []
		for phoneme, error in phonemeset.parse(phonemes, checks):
			if error:
				yield None, None, None, None, None, u'{0} in entry: "{1}"'.format(error, line)
			else:
				arpabet_phonemes.append(phoneme)

		# duplicate and context ordering checks

		key = word.upper()
		position = order_from if context is None else context

		entry_line = u'{0}({1}) {2}'.format(word, context, arpabet_phonemes)
		if entry_line in lines and 'duplicate-entries' in checks:
			yield None, None, None, None, None, u'Duplicate entry: "{2}"'.format(position, expect_position, line)
		elif isinstance(position, int):
			pronunciation = ' '.join(arpabet_phonemes)
			if key in entries:
				expect_position, pronunciations = entries[key]
			else:
				expect_position = order_from
				pronunciations = []
			if position != expect_position and 'context-ordering' in checks:
				yield None, None, None, None, None, u'Incorrect context ordering "{0}" (expected: "{1}") in entry: "{2}"'.format(position, expect_position, line)
			expect_position = expect_position + 1
			if pronunciation in pronunciations:
				if 'duplicate-pronunciations' in checks:
					yield None, None, None, None, None, u'Existing pronunciation in entry: "{2}"'.format(position, expect_position, line)
			else:
				pronunciations.append(pronunciation)
			entries[key] = (expect_position, pronunciations)

		lines[entry_line] = True
		previous_word = word

		# return the parsed entry

		yield word, context, arpabet_phonemes, comment, meta, None
