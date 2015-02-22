# CMU Pronunciation Dictionary Tools

This is a collection of tools for working with the CMU Pronunciation
Dictionary.

## File Format

There are 3 variants of the cmudict dictionary format in use:

  *  `cmudict-weide` is the old dictionary format as maintained by Robert L.
     Weide and others (versions 0.1 through 0.7);
  *  `cmudict` is the current dictionary format as maintained by Alex Rudnicky
     (versions 0.7a and later);
  *  `cmudict-new` is the dictionary format as maintained by Nikolay V.
     Shmyrev.

A line comment starts with `;;;` and spans until the end of the current line.
In the `cmudict-weide` format, a line comment starts with `##`.

An entry has the form `ENTRY PRONUNCIATION`, where `ENTRY` consists of `WORD`
for the primary entry for the word, or `WORD(VARIANT)` for an alternate entry.
The `ENTRY` and `PRONUNCIATION` are separated by two space (` `) characters and
`ENTRY` is in upper case. In the `cmudict-new` format, `ENTRY` and
`PRONUNCIATION` are separated by a single space (` `) character and `ENTRY` is
in lower case.

The `VARIANT` consists of a number from `1` to `9` that denotes an alternate
entry. These are numbered consecutively from `1` in the current cmudict format
and from `2` in the `cmudict-weide` and `cmudict-new` formats.

The `PRONUNCIATION` section consists of Arpabet-based phones separated by a
single space (` `). The casing of the phones depends on the phoneset being
used. The vowels have an additional stress marker, which can be:

  *  `0` for an unstressed vowel;
  *  `1` for a primary stressed vowel;
  *  `2` for a secondary stressed vowel.

An entry may have a comment. These comments start with `#` and span to the end
of the line.

__NOTE:__ The various releases of the cmudict contain various formatting errors
in several entries, where those entries deviate from the format described here.
These will show up as validation warnings when those dictionary versions are
run through `cmudict-tools` with the appropriate validation warnings enabled.

### Metadata

Metadata is not supported in the official CMU dictionary format. However, the
`cmudict-tools` project interprets specifically formatted comments as metadata.
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

#### metadata

The `metadata` metadata key points to a metadata description file containing
the valid `(key,value)` pairs for entry-based metadata.

To test the `(key,value)` extraction for a metadata description file, you can
run:

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
