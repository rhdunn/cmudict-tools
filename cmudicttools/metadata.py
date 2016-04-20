#!/usr/bin/python
# coding=utf-8
#
# Metadata Description File parser.
#
# Copyright (C) 2015-2016 Reece H. Dunn
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
import csv
import json
import codecs
import subprocess

import rdflib

dict_formats = {}

##### CSV Parser ##############################################################

if sys.version_info[0] == 2:
	def read_csvdict(filename):
		with open(filename, 'rb') as f:
			for entry in csv.reader(f):
				yield [x.decode('utf-8') for x in entry]
else:
	def read_csvdict(filename):
		with open(filename, 'rb') as f:
			for entry in csv.reader(codecs.iterdecode(f, 'utf-8')):
				yield entry

def parse_csv(filename):
	columns = None
	for entry in read_csvdict(filename):
		entry = [ None if x == '' else x for x in entry ]
		if entry[0] == None:
			pass # Comment only line
		elif columns:
			yield dict(zip(columns, entry))
		else:
			columns = entry

##### JSON Parser #############################################################

def parse_json(meta, values=None):
	try:
		return json.loads(meta), []
	except ValueError:
		return None, [u'Invalid JSON: `{0}`'.format(meta)]

dict_formats['json'] = (parse_json, json.dumps)

##### Key-Value Metadata Parser ###############################################

def parse_key_values(data, values=None):
	re_key   = re.compile(r'^[a-zA-Z0-9_\-]+$')
	re_value = re.compile(r'^[^\x00-\x20\x7F-\xFF"]+$')
	errors = []
	meta = {}
	for key, value in [x.split('=') for x in data.strip().split()]:
		if values is not None:
			if not key in values.keys():
				errors.append(u'Invalid metadata key "{0}"'.format(key))
			else:
				isvalid, _ = values[key](value)
				if not isvalid:
					errors.append(u'Invalid metadata value "{0}"'.format(value))
		else:
			if not re_key.match(key):
				errors.append(u'Invalid metadata key "{0}"'.format(key))
			if not re_value.match(value):
				errors.append(u'Invalid metadata value "{0}"'.format(value))

		if key in meta.keys():
			meta[key].append(value)
		else:
			meta[key] = [value]
	return meta, errors

def format_key_values(meta):
	ret = []
	for key, values in sorted(meta.items()):
		ret.extend([u'{0}={1}'.format(key, value) for value in values])
	return ' '.join(ret)

dict_formats['key-value'] = (parse_key_values, format_key_values)

##### Metadata Parsers ########################################################

def parse_rdf_metadata(filename):
	rdf  = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
	skos = rdflib.Namespace('http://www.w3.org/2004/02/skos/core#')

	fmt = rdflib.util.guess_format(filename)
	if not fmt:
		with open(filename, 'rb') as f:
			srcdata = f.read()
		if srcdata.startswith(b'#') or srcdata.startswith(b'@prefix'):
			fmt = 'turtle' # RDF/Turtle
		elif srcdata.startswith(b'<!--') or srcdata.startswith(b'<?xml'):
			fmt = 'xml' # RDF/XML
		else:
			fmt = 'nt' # N-Triples

	graph = rdflib.Graph()
	graph.load(filename, format=fmt)

	metadata = {}
	for scheme, _, _ in graph.triples((None, rdf.type, skos.ConceptScheme)):
		ref = None
		for s, p, o in graph.triples((scheme, None, None)):
			if p == skos.notation:
				ref = str(o)
				metadata[ref] = []
		if not ref:
			continue

		concepts = []
		for concept, _, _ in graph.triples((None, skos.inScheme, scheme)):
			for s, p, o in graph.triples((concept, None, None)):
				if p == skos.notation:
					concepts.append(str(o))
		metadata[ref] = sorted(concepts)
	return metadata

def parse_csv_metadata(filename):
	metadata = {}
	for data in parse_csv(filename):
		if not data['Key'] in metadata.keys():
			metadata[data['Key']] = []
		metadata[data['Key']].append(data['Value'])
	return metadata

def parse(filename):
	if filename.endswith('.csv'):
		return parse_csv_metadata(filename)
	return parse_rdf_metadata(filename)
