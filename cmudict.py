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

phoneme_table = [ # cmudict
	##### VOWELS ##########################################################
	('AA', VOWEL),				# AA	odd	AA D
	('AE', VOWEL),				# AE	at	AE T
	('AH', VOWEL),				# AH	hut	HH AH T
	('AO', VOWEL),				# AO	ought	AO T
	('AW', VOWEL),				# AW	cow	K AW
	('AY', VOWEL),				# AY	hide	HH AY D
	('EH', VOWEL),				# EH	Ed	EH D
	('ER', VOWEL),				# ER	hurt	HH ER T
	('EY', VOWEL),				# EY	ate	EY T
	('IH', VOWEL),				# IH	it	IH T
	('IY', VOWEL),				# IY	eat	IY T
	('OW', VOWEL),				# OW	oat	OW T
	('OY', VOWEL),				# OY	toy	T OY
	('UH', VOWEL),				# UH	hood	HH UH D
	('UW', VOWEL),				# UW	two	T UW
	##### CONSONANTS ######################################################
	('B',  CONSONANT),			# B	be	B IY
	('CH', CONSONANT),			# CH	cheese	CH IY Z
	('D',  CONSONANT),			# D	dee	D IY
	('DH', CONSONANT),			# DH	thee	DH IY
	('F',  CONSONANT),			# F	fee	F IY
	('G',  CONSONANT),			# G	green	G R IY N
	('HH', CONSONANT),			# HH	he	HH IY
	('JH', CONSONANT),			# JH	gee	JH IY
	('K',  CONSONANT),			# K	key	K IY
	('L',  CONSONANT),			# L	lee	L IY
	('M',  CONSONANT),			# M	me	M IY
	('N',  CONSONANT),			# N	knee	N IY
	('NG', CONSONANT),			# NG	ping	P IH NG
	('P',  CONSONANT),			# P	pee	P IY
	('R',  CONSONANT),			# R	read	R IY D
	('S',  CONSONANT),			# S	sea	S IY
	('SH', CONSONANT),			# SH	she	SH IY
	('T',  CONSONANT),			# T	tea	T IY
	('TH', CONSONANT),			# TH	theta	TH EY T AH
	('V',  CONSONANT),			# V	vee	V IY
	('W',  CONSONANT),			# W	we	W IY
	('Y',  CONSONANT),			# Y	yield	Y IY L D
	('Z',  CONSONANT),			# Z	zee	Z IY
	('ZH', CONSONANT),			# ZH	seizure	S IY ZH ER
]

dict_formats = { # {0} = word ; {1} = context ; {2} = phonemes ; {3} = comment
	'cmudict-wade': {
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

def parse(filename, check_trailing_whitespace=True):
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

	re_linecomment = re.compile(r'^(##|;;;)(.*)$')
	re_entry = re.compile(r'^([^ a-zA-Z]?[a-zA-Z0-9\'\.\-\_]*)(\(([1-9])\))?([ \t]+)([^#]+)( #(.*))?[ \t]*$')
	re_word_cmu = re.compile(r'^[^ a-zA-Z]?[A-Z0-9\'\.\-\_]*$') # wade/air
	re_word_new = re.compile(r'^[^ a-zA-Z]?[a-z0-9\'\.\-\_]*$') # nshmyrev
	re_word = None
	re_phonemes = re.compile(r' (?=[A-Z][A-Z]?[0-9]?)')
	re_phoneme_start = re.compile(r'^ [A-Z]')
	valid_phonemes = set()
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
			for cmu, ptype in phoneme_table:
				valid_phonemes.add(cmu)
				if ptype == VOWEL:
					valid_phonemes.add('{0}0'.format(cmu))
					valid_phonemes.add('{0}1'.format(cmu))
					valid_phonemes.add('{0}2'.format(cmu))

		if not re_word.match(word):
			yield None, None, None, None, 'Incorrect word casing in entry: "{0}"'.format(line)

		if m.group(GROUP_SPACING) != spacing:
			yield None, None, None, None, 'Entry needs {0} spaces between word and phoneme: "{1}"'.format(len(spacing), line)

		phonemes = m.group(GROUP_PHONEMES)
		if phonemes.endswith(' ') and check_trailing_whitespace:
			yield None, None, None, None, 'Trailing whitespace in entry: "{0}"'.format(line)

		phonemes = re_phonemes.split(phonemes.strip())
		for phoneme in phonemes:
			if not phoneme in valid_phonemes:
				yield None, None, None, None, 'Invalid phoneme "{0}" in entry: "{1}"'.format(phoneme, line)

		comment = m.group(GROUP_COMMENT) or None
		yield word, m.group(GROUP_CONTEXT), phonemes, comment, None
