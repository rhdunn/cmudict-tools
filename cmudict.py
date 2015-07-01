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

default_sort_key = lambda x: x

try:
	import icu

	unicode_collator = icu.Collator.createInstance()
	unicode_sort_key = unicode_collator.getSortKey
except ImportError:
	unicode_sort_key = None

def create_sort_key(mode):
	if not mode or mode in ['weide', 'air']:
		return default_sort_key
	elif mode in ['unicode']:
		if not unicode_sort_key:
			raise Exception('`unicode` sort not supported (install the `pyicu` module to use this mode)')
		return unicode_sort_key
	raise Exception('Unknown sort type: {0}'.format(mode))

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
	# NOTE: Accept anything for string (`s`) types.
	_types = { 's': lambda x: x, 'i': int, 'f': float }

	def __init__(self, value_type):
		self.value_type = self._types[value_type]

	def __call__(self, value):
		try:
			self.value_type(value)
			return True
		except ValueError:
			return False

class StressType:
	UNSTRESSED = '0'
	PRIMARY_STRESS = '1'
	SECONDARY_STRESS = '2'
	WEAK = 'W'
	SYLLABIC = 'S'
	CONSONANT = 'C'
	PROSODY = 'P'

	@staticmethod
	def types():
		return ['0', '1', '2', 'W', 'S', 'C', 'P']

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
		self.stress_types = {}
		self.phone_types = {}

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
			self.stress_types['{0}0'.format(normalized)] = StressType.UNSTRESSED
			self.stress_types['{0}1'.format(normalized)] = StressType.PRIMARY_STRESS
			self.stress_types['{0}2'.format(normalized)] = StressType.SECONDARY_STRESS
			self.phone_types[normalized] = types
			self.phone_types['{0}0'.format(normalized)] = types
			self.phone_types['{0}1'.format(normalized)] = types
			self.phone_types['{0}2'.format(normalized)] = types
		elif 'schwa' in types:
			self.to_arpabet[phoneme] = normalized
			self.to_arpabet['{0}0'.format(phoneme)] = u'{0}0'.format(normalized)
			self.from_arpabet[normalized] = phoneme
			self.from_arpabet['{0}0'.format(normalized)] = u'{0}0'.format(phoneme)
			self.stress_types[normalized] = StressType.WEAK
			self.stress_types['{0}0'.format(normalized)] = StressType.WEAK
			self.phone_types[normalized] = types
			self.phone_types['{0}0'.format(normalized)] = types
		elif 'syllabic' in types:
			self.to_arpabet[phoneme] = normalized
			self.from_arpabet[normalized] = phoneme
			self.stress_types[normalized] = StressType.SYLLABIC
			self.phone_types[normalized] = types
		elif 'prosody' in types:
			self.to_arpabet[phoneme] = normalized
			self.from_arpabet[normalized] = phoneme
			self.stress_types[normalized] = StressType.PROSODY
			self.phone_types[normalized] = types
		else:
			self.to_arpabet[phoneme] = normalized
			self.from_arpabet[normalized] = phoneme
			self.phone_types[normalized] = types

	def stress_type(self, phoneme):
		return self.stress_types.get(phoneme, StressType.CONSONANT)

	def types(self, phoneme):
		return self.phone_types.get(phoneme, [])

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
		'have-comments': True,
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
		'have-comments': True,
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
		'have-comments': True,
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
		'have-comments': True,
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
	'sphinx': {
		'accent': 'en-US',
		'phoneset': 'cmu',
		'have-comments': False,
		# formatting:
		'entry': '{0}\t{2}\n',
		'entry-context': '{0}({1})\t{2}\n',
		'word': lambda word: word.upper(),
	},
}

parser_warnings = {
	'context-values': 'check context values are numbers',
	'context-ordering': 'check context values are ordered sequentially',
	'duplicate-entries': 'check for matching entries (word, context, pronunciation)',
	'duplicate-pronunciations': 'check for duplicated pronunciations for an entry',
	'entry-spacing': 'check spacing between word and pronunciation',
	'invalid-phonemes': 'check for invalid phonemes',
	'missing-primary-stress': 'check for missing primary stress markers in pronunciations',
	'missing-stress': 'check for missing stress markers',
	'multiple-primary-stress': 'check for multiple primary stress markers in pronunciations',
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
	elif mode in ['weide', 'air', 'unicode']:
		ordered = []
		for word, context, phonemes, comment, metadata, error in entries:
			if not word:
				yield (word, context, phonemes, comment, metadata, error)
				continue
			if mode == 'weide':
				if context:
					keyword = '{0}({1})'.format(word, context)
				else:
					keyword = word
			elif mode in ['air', 'unicode']:
				if context:
					keyword = '{0}!{1}'.format(word, context)
				else:
					keyword = word
			ordered.append((keyword, (word, context, phonemes, comment, metadata, error)))
		sort_key = create_sort_key(mode)
		def sorting(x):
			return sort_key(x[0])
		for keyword, entry in sorted(ordered, key=sorting):
			yield entry
	else:
		raise ValueError('unsupported sort mode: {0}'.format(mode))

def remove_context_entries(entries):
	for word, context, phonemes, comment, metadata, error in entries:
		if not word or not context:
			yield word, context, phonemes, comment, metadata, error

def remove_stress(entries, order_from=0):
	words = Trie()
	for word, context, phonemes, comment, metadata, error in entries:
		if not word:
			yield word, context, phonemes, comment, metadata, error
			continue

		phonemes = [ re.sub(r'[0-3]', '', p) for p in phonemes ]
		if word in words:
			context, pronunciations = words[word]
			if phonemes in pronunciations:
				continue # duplicate pronunciation
		else:
			context = order_from
			pronunciations = [ phonemes ]
		pronunciations.append(phonemes)
		words[word] = (context + 1, pronunciations)
		yield word, context, phonemes, comment, metadata, error

def format_text(dict_format, entries, accent=None, phoneset=None, encoding='windows-1252', input_encoding='windows-1252'):
	fmt = dict_formats[dict_format]
	if not accent:
		accent = fmt['accent']
	if not phoneset:
		phoneset = fmt['phoneset']
	if phoneset == 'ipa':
		encoding = 'utf-8'
	phonemeset = load_phonemes(accent, phoneset)
	metaformatter = None
	for word, context, phonemes, comment, meta, error in entries:
		if error:
			print(error, file=sys.stderr)
			continue
		components = []
		if word:
			components.append('entry')
			word = fmt['word'](word)
		if context:
			components.append('context')
		if comment != None or meta != None:
			if meta != None:
				if word and metaformatter:
					metastring = metaformatter(meta)
				else:
					metastring = metadata.format_key_values(meta)
					if not encoding and 'encoding' in meta.keys():
						encoding = meta['encoding'][0]
					if 'metadata-format' in meta.keys():
						_, metaformatter = metadata.dict_formats[ meta['metadata-format'][0] ]
				if comment:
					comment = u'@@ {0} @@{1}'.format(metastring, comment)
				else:
					comment = u'@@ {0} @@'.format(metastring)
			if fmt['have-comments']:
				components.append('comment')
			elif not word: # line comment
				continue
		if phonemes:
			phonemes = phonemeset.format(phonemes)
		if len(components) == 0:
			print()
		elif encoding:
			printf(fmt['-'.join(components)], encoding, word, context, phonemes, comment)
		else:
			printf(fmt['-'.join(components)], input_encoding, word, context, phonemes, comment)

def format_json(dict_format, entries, accent=None, phoneset=None, encoding='windows-1252', input_encoding='windows-1252'):
	fields = ['word', 'context', 'pronunciation', 'comment', 'metadata', 'error-message']
	need_comma = False
	if not encoding:
		encoding = input_encoding
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

def format(dict_format, entries, accent=None, phoneset=None, encoding='windows-1252', input_encoding='windows-1252'):
	if dict_format in ['json']:
		format_json(dict_format, entries, accent, phoneset, encoding, input_encoding)
	else:
		format_text(dict_format, entries, accent, phoneset, encoding, input_encoding)

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

def parse_comment_string(comment, parser, values=None):
	re_key   = re.compile(r'^[a-zA-Z0-9_\-]+$')
	re_value = re.compile(r'^[^\x00-\x20\x7F-\xFF"]+$')
	if comment.startswith('@@'):
		_, metastring, comment = comment.split('@@')
		meta, errors = parser(metastring, values=values)
		return comment, meta, errors
	return comment, None, []

def parse_festlex(filename, checks, encoding):
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
			comment, meta, errors = parse_comment_string(m.group(1), metadata.parse_key_values)
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
			comment, meta, errors = parse_comment_string(comment, metadata.parse_key_values)
			for message in errors:
				yield line, format, None, None, None, None, None, '{0} in entry: "{1}"'.format(message, line)

		if context == 'nil':
			context = None

		yield line, format, word, context, phonemes, comment, meta, None

def parse_cmudict(filename, checks, encoding):
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
	metaparser = metadata.parse_key_values

	with open(filename, 'rb') as f:
		lines = re.split(b'\r?\n', f.read())
	if len(lines[-1]) == 0:
		lines = lines[:-1]

	for line in lines:
		line = line.decode(encoding)
		if line == '':
			yield line, format, None, None, None, None, None, None
			continue

		comment = None
		m = re_linecomment_weide.match(line)
		if m:
			comment, meta, errors = parse_comment_string(m.group(1), metadata.parse_key_values)
			comment_format = 'cmudict-weide'

		m = re_linecomment_air.match(line)
		if m:
			comment, meta, errors = parse_comment_string(m.group(1), metadata.parse_key_values)
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
				if 'encoding' in meta.keys():
					encoding = meta['encoding'][0]
				if 'metadata-format' in meta.keys():
					metaparser, _ = metadata.dict_formats[ meta['metadata-format'][0] ]
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
			comment, meta, errors = parse_comment_string(comment, metaparser, values=entry_metadata)
			for message in errors:
				yield line, format, None, None, None, None, None, u'{0} in entry: "{1}"'.format(message, line)

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

def parse(filename, warnings=[], order_from=0, accent=None, phoneset=None, encoding='windows-1252', syllable_breaks=True, sort_mode=None):
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

	sort_key = create_sort_key(sort_mode)
	for line, format, word, context, phonemes, comment, meta, error in dict_parser(filename, checks, encoding):
		if error:
			yield None, None, None, None, None, error
			continue

		if not word: # line comment or blank line
			yield None, None, None, comment, meta, None
			if meta and not fmt:
				if 'accent' in meta.keys():
					accent = meta['accent'][0]
				if 'order-from' in meta.keys():
					order_from = int(meta['order-from'][0])
				if 'phoneset' in meta.keys():
					phoneset = meta['phoneset'][0]
				if 'sorting' in meta.keys():
					sort_key = create_sort_key(meta['sorting'][0])
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

		if previous_word and sort_key(word) < sort_key(previous_word) and 'unsorted' in checks:
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
		stress_counts = dict([(t, 0) for t in StressType.types()])
		for phoneme, error in phonemeset.parse(phonemes, checks):
			if error:
				yield None, None, None, None, None, u'{0} in entry: "{1}"'.format(error, line)
			else:
				if syllable_breaks == False and 'syllable' in phonemeset.types(phoneme):
					continue
				arpabet_phonemes.append(phoneme)
				stress_counts[phonemeset.stress_type(phoneme)] += 1

		vowels = stress_counts[StressType.UNSTRESSED] + stress_counts[StressType.PRIMARY_STRESS] + stress_counts[StressType.SECONDARY_STRESS] + stress_counts[StressType.WEAK] + stress_counts[StressType.SYLLABIC]


		if vowels == 1 and stress_counts[StressType.WEAK] == 1: # weak forms (a, the, had, etc.)
			pass
		elif vowels == 1 and stress_counts[StressType.SYLLABIC] == 1: # mmmm, hmmm, etc.
			pass
		elif len(arpabet_phonemes) == 1 and 'fricative' in phonemeset.types(arpabet_phonemes[0]): # shhh, zzzz, etc.
			pass
		elif stress_counts[StressType.PRIMARY_STRESS] == 0:
			if 'missing-primary-stress' in checks:
				yield None, None, None, None, None, u'No primary stress marker in entry: "{0}"'.format(line)
		elif stress_counts[StressType.PRIMARY_STRESS] != 1:
			if 'multiple-primary-stress' in checks:
				yield None, None, None, None, None, u'Multiple primary stress markers in entry: "{0}"'.format(line)

		# duplicate and context ordering checks

		keyword = word.upper()
		position = order_from if context is None else context

		entry_line = u'{0}({1}) {2}'.format(word, context, arpabet_phonemes)
		if entry_line in lines and 'duplicate-entries' in checks:
			yield None, None, None, None, None, u'Duplicate entry: "{2}"'.format(position, expect_position, line)
		elif isinstance(position, int):
			pronunciation = ' '.join(arpabet_phonemes)
			if keyword in entries:
				expect_position, pronunciations = entries[keyword]
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
			entries[keyword] = (expect_position, pronunciations)

		lines[entry_line] = True
		previous_word = word

		# return the parsed entry

		yield word, context, arpabet_phonemes, comment, meta, None
