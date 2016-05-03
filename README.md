# CMU Pronunciation Dictionary Tools

- [Dependencies](#dependencies)
- [Usage](#usage)
    - [Example: Porter Stemmer](#example-porter-stemmer)
    - [Example: Phonetisaurus](#example-phonetisaurus)
    - [Example: Sphinx Dictionary](#example-sphinx-dictionary)
    - [Example: Festival Dictionary](#example-festival-dictionary)
    - [Example: Git Merge Resolution](#example-git-merge-resolution)
- [VIM Syntax File](#vim-syntax-file)
- [CMU Pronunciation Dictionary File Format](#cmu-pronunciation-dictionary-file-format)
    - [Metadata](#metadata)
- [File-Based Metadata](#file-based-metadata)
- [Phone Table File Format](#phone-table-file-format)
- [Metadata Description File Format](#metadata-description-file-format)
    - [CSV Metadata](#csv-metadata)
    - [RDF Metadata](#rdf-metadata)
- [Configuration Options](#configuration-options)
    - [ACCENT](#accent)
    - [FORMAT](#format)
    - [METADATA](#metadata-1)
    - [PHONESET](#phoneset)
    - [SORT](#sort)
    - [TAGSET](#tagset)
    - [WARNING](#warning)
- [License](#license)

----------

This is a collection of tools for working with the CMU Pronunciation
Dictionary.

## Dependencies

| Library | Required? | Description |
|---------|-----------|-------------|
| [pyicu](https://pypi.python.org/pypi/PyICU/) | No | Used for the `unicode` [SORT](#sort) ordering. |
| [rdflib](https://pypi.python.org/pypi/rdflib/) | Yes | Used for the context and metadata tagset parsing. |
| [rdflib-jsonld](https://pypi.python.org/pypi/rdflib-jsonld/) | No | Used for JSON-LD format support in the context and metadata tagset parsing. |

To install these libraries on Debian-based machines (including Ubuntu and Mint), you can run:

	sudo apt-get install python-LIBRARY

On other operating systems, you can run:

	sudo pip install LIBRARY

This will install the `LIBRARY` python package.

## Usage

The `cmudict-tools` program has the following command-line structure:

	cmudict-tools [OPTIONS] COMMAND DICTIONARY
	cmudict-tools [OPTIONS] COMMAND YOURS THEIRS
	cmudict-tools [OPTIONS] COMMAND YOURS THEIRS BASE

The supported `OPTIONS` are:

| `OPTION`                                  | Description |
|-------------------------------------------|-------------|
| `-h`, `--help`                            | Show a help message and exit. |
| `-W` [WARNING](#warning)                  | Enable or disable the specified validation warnings. |
| `--source-accent` [ACCENT](#accent)       | Use `ACCENT` to source the dictionary phonesets. |
| `--source-phoneset` [PHONESET](#phoneset) | Use `PHONESET` to validate the phones in the dictionary. |
| `--accent` [ACCENT](#accent)              | Use `ACCENT` to source the output phonesets. |
| `--phoneset` [PHONESET](#phoneset)        | Use `PHONESET` to validate the phones in the output. |
| `--format` [FORMAT](#format)              | Output the dictionary entries in `FORMAT`. |
| `--sort` [SORT](#sort)                    | Sort the entries using `SORT` ordering. |
| `--order-from ORDER_FROM`                 | Start variants at `ORDER_FROM`, including the initial entry. |
| `--help-warnings`                         | List the available validation warnings. |
| `--input-encoding ENCODING`               | Use `ENCODING` to read the dictionary file in (e.g. `latin1`). |
| `--output-encoding ENCODING`              | Use `ENCODING` to print the entries in (e.g. `latin1`). |
| `--output-context` [TAGSET](#tagset)      | Use the `TAGSET` to format the context entries as. |
| `--remove-context-entries`                | Ignore entries with a context specified. |
| `--remove-duplicate-contexts`             | Remove entries with the same context for a given word, keeping the first context entry. |
| `--remove-syllable-breaks`                | Remove syllable break markers from pronunciations. |
| `--remove-stress`                         | Remove stress markers from pronunciations. |

__NOTE:__ The `--remove-stress` option will remove any duplicate entries that
result from removing the stress markers.

`COMMAND` can be one of:

| `COMMAND`         | Description |
|-------------------|-------------|
| `diff`            | Perform a diff on the dictionary. |
| `merge`           | Perform a merge on the dictionary. |
| `print`           | Format and optionally sort the dictionary. |
| `select=SELECTOR` | Select the item corresponding to `SELECTOR` (see below). |
| `stats`           | Display dictionary statistics. |
| `validate`        | Only perform validation checks. |

The `DICTIONARY` file is auto-detected according to one of the supported input
[FORMAT](#format) values.

The `SELECTOR` value can be:

| `SELECTOR` | Description |
|------------|-------------|
| `word`     | Select the word field of the dictionary. |
| `@KEY`     | Select `KEY` from the metadata section of the dictionary. |
| `A|B`      | Select the value of `A` if present, or `B` if not, where `A` and `B` are `SELECTOR` values themselves. |

For the `diff` and `merge` commands, the following usage modes are supported:

| Arguments           | Description |
|---------------------|-------------|
| `DICTIONARY`        | Use conflict markers to determine `YOURS` and `THEIRS`. |
| `YOURS THEIRS`      | Perform the diff/merge against `YOURS` and `THEIRS`. |
| `YOURS THEIRS BASE` | Perform the diff/merge against `YOURS` and `THEIRS`, using `BASE` as a reference. |

### Example: Porter Stemmer

The `select` command can be used to extract the data used to test a Porter
stemmer algorithm:

	./cmudict-tools select=word cmudict > in.txt
	./cmudict-tools select="@stem|word" cmudict > out.txt

This examples entries to have metadata like:

	BURN  B ER1 N
	BURNING  B ER1 N IH0 NG #@@ stem=BURN @@

### Example: Phonetisaurus

The dictionary can be converted to a form that is usable with
`phonetisaurus-align` by running:

	./cmudict-tools --format=sphinx --remove-context-entries \
		print cmudict > cmudict.lex

Or, if you don't want stresses on vowels:

	./cmudict-tools --format=sphinx --remove-context-entries --remove-stress \
		print cmudict > cmudict.lex

This can then be passed to `phonetisaurus-align` using:

	phonetisaurus-align --input=cmudict.lex --ofile=cmudict.corpus --seq1_del=false

### Example: Sphinx Dictionary

To generate a sphinx4 dictionary you can run:

	./cmudict-tools --format=sphinx --remove-stress \
		print cmudict > cmudict_SPHINX_40

### Example: Festival Dictionary

To generate a festival dictionary you can run:

	./cmudict-tools --format=festlex --output-context=festlex --remove-duplicate-contexts \
		print cmudict > cmudict.scm

### Example: Git Merge Resolution

To configure git to support merging cmudict files, run:

	git config --global merge.tool cmudict
	git config --global mergetool.cmudict.cmd 'cmudict-tools merge $LOCAL $REMOTE $BASE > $MERGED'
	git config --global mergetool.cmudict.trustExitCode true
	git config --global mergetool.cmudict.keepBackup false

Now, when there are merge conflicts from a cmudict format file, you can run:

	git mergetool -t cmudict

You will still need to check the file for conflicts in the case where an entry
has been modified by the local and remote versions. These are denoted by standard
conflict markers, so searching for `<<<<<` will work.

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
| `b:cmudict_format`=[FORMAT](#format)       | `format`=[FORMAT](#format)       | __auto__ | The specific format of the dictionary. |

__NOTE:__ The file-based metadata must occur within the first 5 lines of the
file to be supported by the VIM syntax file.

If no [FORMAT](#format) is specified, its value is determined based on the
content. This logic has rules for the old Weide format as well as the new
formats (both the currently maintained dictionary and `cmudict-new` formats).
Additionally, it detects files containing `Pronunciation Dictionary` within a
`;;;` comment as `cmudict` documents.

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

The content within the metadata block may be in one of the following formats:

1.  `key-value`

    The content within the metadata block is a sequence of space-separated
    `key=value` pairs. A key can occur multiple times, in which case the key
    will have both values.

2.  `json`

    The metadata is a JSON string.

## File-Based Metadata

This is metadata on line comments in the given dictionary format. This must be
in the `key-value` format.

The file-based metadata that `cmudict-tools` understands is:

| Metadata                           | Default        | Description |
|------------------------------------|----------------|-------------|
| `accent`=[ACCENT](#accent)         | `en-US`        | The accent the dictionary is specified in. |
| `context-format`=[TAGSET](#tagset) | __auto__       | Use `TAGSET` to validate context values. |
| `encoding`=`ENCODING`              | `windows-1252` | The character encoding the dictionary entries are encoded in. |
| `format`=[FORMAT](#format)         | __auto__       | The specific format of the dictionary. |
| `metadata-format`=`FORMAT`         | `key-value`    | The format type of entry-based metadata. |
| `metadata`=[METADATA](#metadata)   |                | The specification for entry-based metadata. |
| `order-from`=`ORDER_FROM`          | 0              | Start variants at `ORDER_FROM`, including the initial entry. |
| `phoneset`=[PHONESET](#phoneset)   | `cmu`          | The phoneset used to transcribe the phones in. |
| `sorting`=[SORT](#sort)            | `none`         | Sort the entries using `SORT` ordering. |

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

The `Type` field supports any values that can be separated using a `;`. The
following values are given special meanings:

  *  `schwa` -- A weak vowel that can have an optional unstressed (`0`) stress
     marker in pronunciations.

  *  `vowel` -- A vowel that must have a stress marker in pronunciations.

For example:

	Arpabet,Normalized,IPA,Type,Phone Sets
	AA,,ɑ,vowel,arpabet;ipa;cmu;festvox;cepstral;timit
	AE,,æ,vowel,arpabet;ipa;cmu;festvox;cepstral;timit

## Metadata Description File Format

| File Type | Metadata Format               |
|-----------|-------------------------------|
| CSV       | [CSV Metadata](#csv-metadata) |
| JSON-LD   | [RDF Metadata](#rdf-metadata) |
| Microdata | [RDF Metadata](#rdf-metadata) |
| N-Quads   | [RDF Metadata](#rdf-metadata) |
| N-Triples | [RDF Metadata](#rdf-metadata) |
| N3        | [RDF Metadata](#rdf-metadata) |
| RDF/XML   | [RDF Metadata](#rdf-metadata) |
| RDFa      | [RDF Metadata](#rdf-metadata) |
| TriX      | [RDF Metadata](#rdf-metadata) |
| Turtle    | [RDF Metadata](#rdf-metadata) |

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
The labels are defined using `skos:notation` predicates. A `value` is
associated with a `key` using the `skos:inScheme` predicate. All other metadata
triples are currently ignored.

For example, to support `key=value` a minimal RDF Turtle file is:

	@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

	<#> a skos:ConceptScheme ; skos:notation "key" .

	<#val> a skos:Concept ; skos:notation "value" ; skos:inScheme <#> .

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
| `sphinx`        | no    | yes    | no       | no  | The lexicon format used by sphinx4, phonetisaurus, etc. |
| `json`          | no    | yes    | no       | no  | JSON formatted entries and validation errors. |

### METADATA

The `METADATA` value points to a metadata description file containing the valid
`(key,value)` pairs for entry-based metadata.

To test the `(key,value)` extraction for a metadata description file, you can
run:

	python metadata.py <metadata-description-file>

This will output JSON text, for example:

	{"key1": ["value1", "value2"], "key2": ["value3"]}

Additionally, `@type:key` can be used to specify keys that have arbitrary values
of a regular format. Valid types are:

  *  `s` for string values;
  *  `i` for integer numbers (e.g. `274`);
  *  `f` for floating point numbers (e.g. `56.46325`).

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

  *  `unicode` to use the new-style sort order (group variants next to their root
     entry) with words sorted using the Unicode Collation Algorithm (UCA) to
     provide a more natural grouping of accented characters, etc.;

  *  `weide` to use the old-style sort order (simple ASCII character ordering).

### TAGSET

The supported `TAGSET` values are:

| `TAGSET`     | Description |
|--------------|-------------|
| `cainteoir`  | The Part-of-Speech tagset used by Cainteoir Text-to-Speech and related projects. |
| `cmu`        | The context values used by CMU pronunciation dictionaries. |
| `festlex`    | The Part-of-Speech tagset used by `festlex-CMU`. |
| `upenn`      | The Part-of-Speech tagset used by the Penn Treebank project. |
| `wp20`       | A Part-of-Speech tagset defined by the Festival Text-to-Speech project that is a subset of wp39. |
| `wp39`       | A Part-of-Speech tagset defined by the Festival Text-to-Speech project. |
| __filename__ | A metadata file containing the tagset definition. |

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
| `missing-primary-stress`   | Check for missing primary stress markers. |
| `missing-stress`           | Check for missing stress markers. |
| `multiple-primary-stress`  | Check for multiple primary stress markers. |
| `phoneme-spacing`          | Check for a single space between phonemes. |
| `trailing-whitespace`      | Check for trailing whitespaces. |
| `unsorted`                 | Check if a word is not sorted correctly. |
| `word-casing`              | Check for consistent word casing. |

__NOTE:__ Currently, the `unsorted` check does not recognise the `weide`
sort order.

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

It is also possible to locally disable warnings when using the JSON-based line
metadata format using the `disable-warnings` metadata key as a list of the
warnings to disable. For example:

	IS  IH0 Z #@@{ "disable-warnings": ["missing-primary-stress"] }@@

## License

The CMU Pronunciation Dictionary Tools are released under the GPL version 3 or
later license.

Copyright (C) 2015-2016 Reece H. Dunn
