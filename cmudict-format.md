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
