# CMU Pronunciation Dictionary Tools

- [Usage](#usage)
- [CMU Pronunciation Dictionary File Format](#cmu-pronunciation-dictionary-file-format)
  - [Metadata](#metadata)
- [File-Based Metadata](#file-based-metadata)
  - [format](#format)
  - [metadata](#metadata-1)
- [Phone Table File Format](#phone-table-file-format)
- [CSV Metadata Description File Format](#csv-metadata-description-file-format)
- [RDF Metadata Description File Format](#rdf-metadata-description-file-format)
- [License](#license)

----------

This is a collection of tools for working with the CMU Pronunciation
Dictionary.

## Usage

The `cmudict-tools` program has the following command-line structure:

	cmudict-tools [OPTIONS] COMMAND DICTIONARY

`COMMAND` can be one of:

| `print`    | Format and optionally sort the dictionary. |
| `validate` | Only perform validation checks. |

The supported `OPTIONS` are:

| `-h`, `--help`               | Show a help message and exit. |
| `-W WARNING`                 | Enable or disable the specified validation warnings. |
| `--source-accent ACCENT`     | Use `ACCENT` to source the dictionary phonesets. |
| `--source-phoneset PHONESET` | Use `PHONESET` to validate the phones in the dictionary. |
| `--accent ACCENT`            | Use `ACCENT` to source the outpur phonesets. |
| `--phoneset PHONESET`        | Use `PHONESET` to validate the phones in the output. |
| `--format FORMAT`            | Output the dictionary entries in `FORMAT`. |
| `--sort SORT`                | Sort the entries using `SORT` ordering. |
| `--order-from ORDER_FROM`    | Start variants at `ORDER_FROM`, including the initial entry. |
| `--help-warnings`            | List the available validation warnings. |
| `--input-encoding ENCODING`  | Use `ENCODING` to read the dictionary file in (e.g. `latin1`). |
| `--output-encoding ENCODING` | Use `ENCODING` to print the entries in (e.g. `latin1`). |

The supported `DICTIONARY` (input) and `FORMAT` (output) values are:

| Format          | Input | Output | Description |
|-----------------|-------|--------|-------------|
| `cmudict`       | yes   | yes    | The current dictionary format as maintained by Alex Rudnicky (versions 0.7a and later). |
| `cmudict-weide` | yes   | yes    | The old dictionary format as maintained by Robert L. Weide and others (versions 0.1 through 0.7). |
| `cmudict-new`   | yes   | yes    | The dictionary format as maintained by Nikolay V. Shmyrev. |
| `festlex`       | yes   | yes    | The festival lexicon format for Scheme (`*.scm`) files. |
| `json`          | no    | yes    | JSON formatted entries and validation errors. |

The supported `ACCENT` values are:

  *  `en-US` to use the American English phone table;
  *  `en-GB-x-rp` to use the Received Pronunciation British English phone table;
  *  a CSV file to use phonesets defined in that CSV file (see Phone Table File
     Format for a description of this file format).

The supported `PHONESET` values depend on the phone table used. For the `en-US`
and `en-GB-x-rp` phone tables defined by `cmudict-tools`, the supported
phonesets are:

| Phoneset   | en-US | en-GB-x-rp | Description |
|------------|-------|------------|-------------|
| `arpabet`  | yes   | yes        | An expanded Arpabet-based phoneset. |
| `cepstral` | yes   | yes        | The phoneset used by the Cepstral Text-to-Speech program. |
| `cmu`      | yes   | no         | The phoneset used by the official cmudict dictionary. |
| `festvox`  | yes   | no         | The phoneset used by the festlex-cmu dictionary. |
| `ipa`      | yes   | yes        | Use an IPA (International Phonetic Alphabet) transcription. |
| `timit`    | yes   | no         | The phoneset used by the TIMIT database. |

The supported `SORT` values are:

  *  `air` to use the new-style sort order (group variants next to their root
     entry);
  *  `none` to leave the entries in the order they are in the dictionary;
  *  `weide` to use the old-style sort order (simple ASCII character ordering).

## CMU Pronunciation Dictionary File Format

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

## File-Based Metadata

This is metadata on line comments in the given dictionary format. This metadata
is used to control the `cmudict-tools` behaviour.

### format

The `format` metadata key overrides the auto-detected file format. It only
applies to the cmudict-based formats.

### metadata

The `metadata` metadata key points to a metadata description file containing
the valid `(key,value)` pairs for entry-based metadata.

To test the `(key,value)` extraction for a metadata description file, you can
run:

	python metadata.py <metadata-description-file>

This will output JSON text, for example:

	{"key1": ["value1", "value2"], "key2": ["value3"]}

## Phone Table File Format

This is a CSV document with the first line containing the titles of each field.
At a minimum, it needs to support the following fields:

  *  `Arpabet` is the phone using an upper-case Arpabet transcription,
     excluding the stress marker;
  *  `Normalized` is the optional canonical form for phonesets that use a
     different transcription for a given phone;
  *  `IPA` is the International Phonetic Alphabet (IPA) transcription for the
     phone excluding stress markers;
  *  `Type` is the phone type (see below) of the given phone;
  *  `Phone Sets` is a semi-colon (`;`) separated list of phonesets that
     support this phone.

The supported values for the `Type` field are:

  *  `vowel` to indicate a phone that can have a stress marker;
  *  `consonant` to indicate a phone that cannot have a stress marker;
  *  `schwa` to indicate a phone that can either have no stress marker, or the
     unstressed (`0`) stress marker.

For example:

	Arpabet,Normalized,IPA,Type,Phone Sets
	AA,,ɑ,vowel,arpabet;ipa;cmu;festvox;cepstral;timit
	AE,,æ,vowel,arpabet;ipa;cmu;festvox;cepstral;timit

## CSV Metadata Description File Format

This is a CSV document with the first line containing the titles of each field.
At a minimum, it needs to support the following fields:

  *  `Key` is the metadata key;
  *  `Value` is an allowed value for the metadata key.

For example:

	Key,Value
	key1,value1
	...
	keyN,valueN

## RDF Metadata Description File Format

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
