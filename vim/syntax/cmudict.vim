" Vim syntax file
" Language:	Dictionary Entries
" Filenames:    cmudict
" Maintainer:	Reece H. Dunn <msclrhd@gmail.com>
" Last Change:	2015 Feb 23

" Quit when a (custom) syntax file was already loaded
if exists("b:current_syntax")
  finish
endif

syn match	cmudictPhoneStress	"[0-9]"
syn match	cmudictPhone		" [A-Za-z]\=[A-Za-z@]\=R\=[0-9]\=" contains=cmudictPhoneStress

syn region	cmudictVariant		start='(' end=')'

syn region	cmudictEntryComment	start='#' end='$'

syn match	cmudictEntry		"^[^A-Za-z0-9]\=[^ \t(#]\+"

syn match	cmudictPronunciation	"  [a-zA-Z0-9@ \t]\+" contains=cmudictPhone

syn region	cmudictLineComment	start='^;;;' end='$'
syn region	cmudictLineComment	start='^##' end='$'

" Define the default highlighting.
" Only used when an item doesn't have highlighting yet
hi def link cmudictEntryComment		Comment
hi def link cmudictLineComment		Comment
hi def link cmudictComment		Comment
hi def link cmudictEntry		Identifier
hi def link cmudictVariant		Statement
hi def link cmudictPhoneStress		Constant
hi def link cmudictPronunciation	Error
hi def link cmudictPhone		Type

let b:current_syntax = "cmudict"
" vim: ts=8
