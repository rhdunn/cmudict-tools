# CMU Pronunciation Dictionary Tools

- [Usage](#usage)
  - [Warnings](#warnings)
- [VIM Syntax File](#vim-syntax-file)
- [CMU Pronunciation Dictionary File Format](#cmu-pronunciation-dictionary-file-format)
  - [Metadata](#metadata)
- [File-Based Metadata](#file-based-metadata)
  - [format](#format)
  - [metadata](#metadata-1)
- [Phone Table File Format](#phone-table-file-format)
- [Metadata Description File Format](#metadata-description-file-format)
  - [CSV Metadata](#csv-metadata)
  - [RDF Metadata](#rdf-metadata)
- [Configuration Options](#configuration-options)
  - [ACCENT](#accent)
  - [FORMAT](#format-1)
  - [PHONESET](#phoneset)
  - [SORT](#sort)
  - [WARNING](#warning)
- [License](#license)

----------

This is a collection of tools for working with the CMU Pronunciation
Dictionary.

## Usage

The `cmudict-tools` program has the following command-line structure:

	cmudict-tools [OPTIONS] COMMAND DICTIONARY

The supported `OPTIONS` are:

| `OPTION`                                  | Description |
|-------------------------------------------|-------------|
| `-h`, `--help`                            | Show a help message and exit. |
| `-W` [WARNING](#warning)                  | Enable or disable the specified validation warnings. |
| `--source-accent` [ACCENT](#accent)       | Use `ACCENT` to source the dictionary phonesets. |
| `--source-phoneset` [PHONESET](#phoneset) | Use `PHONESET` to validate the phones in the dictionary. |
| `--accent` [ACCENT](#accent)              | Use `ACCENT` to source the outpur phonesets. |
| `--phoneset` [PHONESET](#phoneset)        | Use `PHONESET` to validate the phones in the output. |
| `--format` [FORMAT](#format-1)            | Output the dictionary entries in `FORMAT`. |
| `--sort` [SORT](#sort)                    | Sort the entries using `SORT` ordering. |
| `--order-from ORDER_FROM`                 | Start variants at `ORDER_FROM`, including the initial entry. |
| `--help-warnings`                         | List the available validation warnings. |
| `--input-encoding ENCODING`               | Use `ENCODING` to read the dictionary file in (e.g. `latin1`). |
| `--output-encoding ENCODING`              | Use `ENCODING` to print the entries in (e.g. `latin1`). |

`COMMAND` can be one of:

| `COMMAND`  | Description |
|------------|-------------|
| `print`    | Format and optionally sort the dictionary. |
| `validate` | Only perform validation checks. |

The `DICTIONARY` file is auto-detected according to one of the supported input
[FORMAT](#format-1) values.

## VIM Syntax File

The `cmudict-tools` project provides a syntax highlighting file for
cmudict-style dictionaries.

You can install the files to a VIM install by running:

	make VIMDIR=<path-to-vim> vim

Alternatively, if your system supports VIM addons (e.g. Debian Linux), you can
install the files by running:

	make vim_plugin

which installs the files to `/usr/share/vim`. If the addon files are not in
this location, you need to point `VIMDIR` to the `addons` directory and
`VIMPLUGINDIR` to the `registry` directory.

Once installed, it will automatically highlight files named `cmudict`. You can
explicitly enable highlighting by using the VIM command:

	set ft=cmudict

The following variables and [file-based metadata](#metadata) are supported:

| Variable                                   | Metadata                         | Default  | Description |
|--------------------------------------------|----------------------------------|----------|-------------|
| `b:cmudict_accent`=[ACCENT](#accent)       | `accent`=[ACCENT](#accent)       | `en-US`  | The accent the dictionary is specified in. |
| `b:cmudict_phoneset`=[PHONESET](#phoneset) | `phoneset`=[PHONESET](#phoneset) | `cmu`    | The phoneset used to transcribe the phones in. |
| `b:cmudict_format`=[FORMAT](#format-1)     | `format`=[FORMAT](#format-1)     | __auto__ | The specific format of the dictionary. |

__NOTE:__ The file-based metadata must occur within the first 5 lines of the
file to be supported by the VIM syntax file.

If no [FORMAT](#format-1) is specified, its value is based on the filename as follows:

| Filename                 | Example        | [FORMAT](#format-1) |
|--------------------------|----------------|---------------------|
| `cmudict\.0\.[1-6][a-z]` | `cmudict.0.6d` | `cmudict-weide`     |
| `cmudict\.(vp|dict)`     | `cmudict.dict` | `cmudict-new`       |
| `*`                      | `cmudict-0.7b` | `cmudict`           |

__NOTE:__ You need to set the variables before setting the filetype. For example:

	let b:cmudict_phoneset="arpabet"
	set ft=cmudict

Alternatively, you can set this information as file-based metadata. For example:

	;;;@@ phoneset=arpabet @@

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
applies to the cmudict-based formats. See [FORMAT](#format-1) for supported
values.

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

## Metadata Description File Format

| File Type | Metadata Format               |
|-----------|-------------------------------|
| CSV       | [CSV Metadata](#csv-metadata) |
| Turtle    | [RDF Metadata](#rdf-metadata) |
| RDF/XML   | [RDF Metadata](#rdf-metadata) |
| N-Triples | [RDF Metadata](#rdf-metadata) |

__NOTE:__ The Turtle and RDF/XML formats require the `rapper` command-line
application. This is so those formats can be converted to the N-Triple format.

### CSV Metadata

This is a CSV document with the first line containing the titles of each field.
At a minimum, it needs to support the following fields:

  *  `Key` is the metadata key;
  *  `Value` is an allowed value for the metadata key.

For example:

	Key,Value
	key1,value1
	...
	keyN,valueN

### RDF Metadata

This is an RDF document using the SKOS ontology.

A `key` is defined as a `skos:ConceptScheme` and a `value` as a `skos:Concept`.
The labels are defined using `skos:prefLabel` predicates. A `value` is
associated with a `key` using the `skos:inScheme` predicate. All other metadata
triples are ignored.

For example, to support `key=value` a minimal RDF Turtle file is:

	@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

	<#> a skos:ConceptScheme ; skos:prefLabel "key" .

	<#val> a skos:Concept ; skos:prefLabel "value" ; skos:inScheme <#> .

## Configuration Options

These are the various valid values used by the command-line options, VIM syntax
file and file-based metadata. See the appropriate sections on how to specify
these values.

### ACCENT

The supported `ACCENT` values are:

  *  `en-US` to use the American English phone table;
  *  `en-GB-x-rp` to use the Received Pronunciation British English phone table;
  *  a CSV file to use phonesets defined in that CSV file (see Phone Table File
     Format for a description of this file format).

### FORMAT

The supported `FORMAT` values are:

| Format          | Input | Output | Metadata | VIM | Description |
|-----------------|-------|--------|----------|-----|-------------|
| `cmudict`       | yes   | yes    | yes      | yes | The current dictionary format as maintained by Alex Rudnicky (versions 0.7a and later). |
| `cmudict-weide` | yes   | yes    | yes      | yes | The old dictionary format as maintained by Robert L. Weide and others (versions 0.1 through 0.7). |
| `cmudict-new`   | yes   | yes    | yes      | yes | The dictionary format as maintained by Nikolay V. Shmyrev. |
| `festlex`       | yes   | yes    | no       | no  | The festival lexicon format for Scheme (`*.scm`) files. |
| `json`          | no    | yes    | no       | no  | JSON formatted entries and validation errors. |

### PHONESET

The supported `PHONESET` values depend on the phone table used. For the `en-US`
and `en-GB-x-rp` phone tables defined by `cmudict-tools`, the supported
phonesets are:

| `PHONESET` | `ACCENT=en-US` | `ACCENT=en-GB-x-rp` | Description |
|------------|----------------|---------------------|-------------|
| `arpabet`  | yes            | yes                 | An expanded Arpabet-based phoneset. |
| `cepstral` | yes            | yes                 | The phoneset used by the Cepstral Text-to-Speech program. |
| `cmu`      | yes            | no                  | The phoneset used by the official cmudict dictionary. |
| `festvox`  | yes            | no                  | The phoneset used by the festlex-cmu dictionary. |
| `ipa`      | yes            | yes                 | Use an IPA (International Phonetic Alphabet) transcription. |
| `timit`    | yes            | no                  | The phoneset used by the TIMIT database. |

__NOTE:__ The VIM syntax file does not support `ipa` phoneset validation.

### SORT

The supported `SORT` values are:

  *  `air` to use the new-style sort order (group variants next to their root
     entry);
  *  `none` to leave the entries in the order they are in the dictionary;
  *  `weide` to use the old-style sort order (simple ASCII character ordering).

### WARNING

The supported `WARNING` values are:

| `WARNING`                  | Description |
|----------------------------|-------------|
| `context-ordering`         | Check context values are ordered sequentially. |
| `context-values`           | Check context values are numbers. |
| `duplicate-entries`        | Check for matching entries (word, context, pronunciation). |
| `duplicate-pronunciations` | Check for duplicated pronunciations for an entry. |
| `entry-spacing`            | Check spacing between word and pronunciation. |
| `invalid-phonemes`         | Check for invalid phonemes. |
| `missing-stress`           | Check for missing stress markers. |
| `phoneme-spacing`          | Check for a single space between phonemes. |
| `trailing-whitespace`      | Check for trailing whitespaces. |
| `unsorted`                 | Check if a word is not sorted correctly. |
| `word-casing`              | Check for consistent word casing. |

If `warn` is used, the option is enabled. If `no-warn` is used, the option
is disabled.

The following values have a special behaviour, and cannot be used with the
`no-` prefix:

| `WARNING` | Description |
|-----------|-------------|
| `all`     | Enable all warnings.  |
| `none`    | Disable all warnings. |

The order is important, as the warning set is tracked incrementally. This
allows things like the following combinations:

| Example                     | Description                               |
|-----------------------------|-------------------------------------------|
| `-Wnone -Winvalid-phonemes` | Only use the `invalid-phonemes` warning.  |
| `-Wall -Wno-missing-stress` | Use all warnings except `missing-stress`. |

## License

The CMU Pronunciation Dictionary Tools are released under the GPL version 3 or
later license.

Copyright (C) 2015 Reece H. Dunn
