# CMU Pronunciation Dictionary File Format

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

## Metadata

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
