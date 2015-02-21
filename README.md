# CMU Pronunciation Dictionary Tools

This is a collection of tools for working with the CMU Pronunciation
Dictionary.

## File Format

A line comment starts with `;;;` and spans until the end of the current line.

An entry has the form `ENTRY  PRONUNCIATION`, where `ENTRY` consists of `WORD`
for the primary entry for the word, or `WORD(VARIANT)` for an alternate entry.

The `VARIANT` consists of a number from `1` to `9` that denotes an alternate
entry. These are numbered consecutively from `1`.

The `PRONUNCIATION` section consists of Arpabet-based phones separated by a
single space (` `). The vowels have an additional stress marker, which can be:

  *  `0` for an unstressed vowel;
  *  `1` for a primary stressed vowel;
  *  `2` for a secondary stressed vowel.

An entry may have a comment. These comments start with `#` and span to the end
of the line.

### Metadata

Metadata is not supported in the official CMU dictionary format. However, the
cmudict-tools project interprets specifically formatted comments as metadata.
This allows additional information to be provided in a way that is compatible
with existing cmudict tools.

Metadata occurs in line comments for file-based metadata, or entry comments for
entry-based metadata. The metadata section of the comment starts and ends with
`@@`. The `@@` must be at the start of the comment (i.e. no spaces or other
characters) for it to be recognised as metadata. Any text after the metadata is
treated as a regular comment.

The content within the metadata block is a sequence of space-separated
`key=value` pairs. A key can occur multiple times, in which case the key will
have both values.

### File-Based Metadata

#### format

The `format` metadata key overrides the auto-detected file format. It only
applies to the cmudict-based formats.

### Entry-Based Metadata

The valid `(key,value)` pairs for entry-based metadata is defined in a metadata
description file.

To test the `(key,value)` extraction, you can run:

	python metadata.py <metadata-description-file>

This will output JSON text, for example:

	{"key1": ["value1", "value2"], "key2": ["value3"]}

## CSV Metadata Description Files

This is a CSV document with the following minimal structure:

	Key,Value
	key1,value1
	...
	keyN,valueN

Additional fields are ignored, but must have a unique title label.

## RDF Metadata Description Files

This is an RDF document (turtle, RDF/XML or N-Triples) using the SKOS ontology.
In order to parse these documents, the `rapper` tool is needed.

A `key` is defined as a `skos:ConceptScheme` and a `value` as a `skos:Concept`.
The labels are defined using `skos:prefLabel` predicates. A `value` is
associated with a `key` using the `skos:inScheme` predicate. All other metadata
triples are ignored.

For example, to support `key=value` a minimal RDF Turtle file is:

	@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

	<#> a skos:ConceptScheme ; skos:prefLabel "key" .

	<#val> a skos:Concept ; skos:prefLabel "value" ; skos:inScheme <#> .

## License

The CMU Pronunciation Dictionary Tools are released under the GPL version 3 or
later license.

Copyright (C) 2015 Reece H. Dunn
