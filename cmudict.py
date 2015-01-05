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

phoneme_table = [ # cmudict
	##### VOWELS ##########################################################
	('AA'), ('AA0'), ('AA1'), ('AA2'),	# AA	odd	AA D
	('AE'), ('AE0'), ('AE1'), ('AE2'),	# AE	at	AE T
	('AH'), ('AH0'), ('AH1'), ('AH2'),	# AH	hut	HH AH T
	('AO'), ('AO0'), ('AO1'), ('AO2'),	# AO	ought	AO T
	('AW'), ('AW0'), ('AW1'), ('AW2'),	# AW	cow	K AW
	('AY'), ('AY0'), ('AY1'), ('AY2'),	# AY	hide	HH AY D
	('EH'), ('EH0'), ('EH1'), ('EH2'),	# EH	Ed	EH D
	('ER'), ('ER0'), ('ER1'), ('ER2'),	# ER	hurt	HH ER T
	('EY'), ('EY0'), ('EY1'), ('EY2'),	# EY	ate	EY T
	('IH'), ('IH0'), ('IH1'), ('IH2'),	# IH	it	IH T
	('IY'), ('IY0'), ('IY1'), ('IY2'),	# IY	eat	IY T
	('OW'), ('OW0'), ('OW1'), ('OW2'),	# OW	oat	OW T
	('OY'), ('OY0'), ('OY1'), ('OY2'),	# OY	toy	T OY
	('UH'), ('UH0'), ('UH1'), ('UH2'),	# UH	hood	HH UH D
	('UW'), ('UW0'), ('UW1'), ('UW2'),	# UW	two	T UW
	##### CONSONANTS ######################################################
	('B'),					# B	be	B IY
	('CH'),					# CH	cheese	CH IY Z
	('D'),					# D	dee	D IY
	('DH'),					# DH	thee	DH IY
	('F'),					# F	fee	F IY
	('G'),					# G	green	G R IY N
	('HH'),					# HH	he	HH IY
	('JH'),					# JH	gee	JH IY
	('K'),					# K	key	K IY
	('L'),					# L	lee	L IY
	('M'),					# M	me	M IY
	('N'),					# N	knee	N IY
	('NG'),					# NG	ping	P IH NG
	('P'),					# P	pee	P IY
	('R'),					# R	read	R IY D
	('S'),					# S	sea	S IY
	('SH'),					# SH	she	SH IY
	('T'),					# T	tea	T IY
	('TH'),					# TH	theta	TH EY T AH
	('V'),					# V	vee	V IY
	('W'),					# W	we	W IY
	('Y'),					# Y	yield	Y IY L D
	('Z'),					# Z	zee	Z IY
	('ZH'),					# ZH	seizure	S IY ZH ER
]

dict_formats = { # {0} = word ; {1} = context ; {2} = phonemes ; {3} = comment
	'cmudict-wade': {
		'comment': '##{3}',
		'entry': '{0}  {2}',
		'entry-context': '{0}({1})  {2}',
		'entry-context-comment': '{0}({1})  {2}',
		'entry-comment': '{0}  {2}',
		'phonemes': lambda phonemes: ' '.join(phonemes),
		'word': lambda word: word.upper(),
	},
	'cmudict': {
		'comment': ';;;{3}',
		'entry': '{0}  {2}',
		'entry-comment': '{0}  {2}',
		'entry-context': '{0}({1})  {2}',
		'entry-context-comment': '{0}({1})  {2}',
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

def parse(filename):
	"""
		Parse the entries in the cmudict file.

		The return value is of the form:
			(word, context, phonemes, comment, error)
	"""
	re_linecomment = re.compile(r'^(##|;;;)(.*)$')
	re_entry_cmu = re.compile(r'^([^ a-zA-Z]?[A-Z0-9\'\.\-\_]*)(\(([1-9])\))? ([A-Z012 ]+)(())$') # wade/air
	re_entry_new = re.compile(r'^([^ a-zA-Z]?[a-z0-9\'\.\-\_]*)(\(([1-9])\))?( [A-Z012 ]+)( #(.*))?$') # nshmyrev
	re_entry = None
	re_phonemes = re.compile(r' (?=[A-Z][A-Z]?[0-9]?)')
	valid_phonemes = set()
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
				valid_phonemes = set([p for p in phoneme_table])
			else:
				re_entry = re_entry_cmu
				valid_phonemes = set([p for p in phoneme_table])

		m = re_entry.match(line)
		if not m:
			yield None, None, None, None, 'Unsupported entry: "{0}"'.format(line)
			continue

		phonemes = re_phonemes.split(m.group(4))
		if phonemes[0] == '':
			phonemes = phonemes[1:]
		else:
			yield None, None, None, None, 'Entry needs 2 spaces between word and phoneme: "{0}"'.format(line)

		for phoneme in phonemes:
			if not phoneme in valid_phonemes:
				yield None, None, None, None, 'Invalid phoneme "{0}" in entry: "{1}"'.format(phoneme, line)

		yield m.group(1), m.group(3), phonemes, m.group(6), None
