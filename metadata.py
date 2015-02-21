#!/usr/bin/python
# coding=utf-8
#
# Resource Description Framework (RDF) based metadata Python API.
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
import re
import sys
import subprocess

##### RDF Object Model ########################################################

class Resource:
	pass

class IRI(Resource):
	def __init__(self, data):
		self.href = data[0]

	def __repr__(self):
		return 'IRI({0})'.format(self.href)

class Namespace:
	def __init__(self, prefix, base):
		self.prefix = prefix
		self.base = base

foaf = Namespace('foaf', 'http://xmlns.com/foaf/0.1/')
org  = Namespace('org',  'http://www.w3.org/ns/org#')
rdf  = Namespace('rdf',  'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
skos = Namespace('skos', 'http://www.w3.org/2004/02/skos/core#')

class BNode(Resource):
	def __init__(self, data):
		self.name = data[0]

	def __repr__(self):
		return 'BNode({0})'.format(self.name)

class Literal:
	def __init__(self, data):
		self.text = data[0]
		self.lang = data[1]
		self.datatype = IRI(data[2]) if data[2] else None

	def __repr__(self):
		if self.lang:
			return 'Literal({0}|lang={1})'.format(self.text, self.lang)
		elif self.datatype:
			return 'Literal({0}|datatype={2})'.format(self.text, self.datatype)
		else:
			return 'Literal({0})'.format(self.text)

class Graph:
	def __init__(self):
		self.triples = []

	def add_triple(self, sub, pred, obj):
		self.triples.append((sub, pred, obj))

##### RDF Metadata Parser #####################################################

tokens = [
	(IRI, re.compile(r'^<([^>]*)>')),
	(Literal, re.compile(r'"([^"]*)"@([^ \t]+)()')), # language literal
	(Literal, re.compile(r'"([^"]*)"()\^\^(<([^>]*)>)')), # datatype literal
	(Literal, re.compile(r'"([^"]*)"()()')),
	(BNode, re.compile(r'_:([^ \t]+)')),
	(None, re.compile(r'\s+')),
	(None, re.compile(r'\.')),
]

def parse_ntriple(triple):
	while triple != '':
		matched = False
		for token, matcher in tokens:
			m = matcher.match(triple)
			if m:
				if token:
					yield token(m.groups())
				triple = triple[m.end()+1:]
				matched = True
		if not matched:
			raise Exception('Unknown data in N-Triple output: {0}'.format(triple))

def parse_rdf(filename, input_format=None):
	with open(filename, 'rb') as f:
		srcdata = f.read()

	if not input_format:
		if srcdata.startswith(b'#') or srcdata.startswith(b'@prefix'):
			input_format = 'turtle'
		elif srcdata.startswith(b'<!--') or srcdata.startswith(b'<?xml'):
			input_format = 'rdfxml'
		else:
			input_format = 'ntriples'

	graph = Graph()

	rapper = subprocess.Popen(['rapper', '-', filename, '--input', input_format, '--output', 'ntriples'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = rapper.communicate(input=srcdata)
	for triple in stdout.decode('utf-8').split('\n'):
		data = list(parse_ntriple(triple))
		if len(data) == 0:
			continue
		graph.add_triple(*data)
	return graph

##### Command-Line Interface ##################################################

if __name__ == '__main__':
	graph = parse_rdf(sys.argv[1])
	for s, p, o in graph.triples:
		print((s, p, o))
