" Vim syntax file
" Language:	Dictionary Entries
" Filenames:    cmudict
" Maintainer:	Reece H. Dunn <msclrhd@gmail.com>
" Last Change:	2015 Feb 23

" Quit when a (custom) syntax file was already loaded
if exists("b:current_syntax")
  finish
endif

if !exists("cmudict_accent")
  let cmudict_accent = 'en-US'
endif

if !exists("cmudict_phoneset")
  let cmudict_phoneset = 'cmu'
endif

syn match	cmudictPhoneStress	"[0-9]"

if cmudict_accent == 'en-US'
  if cmudict_phoneset == 'arpabet'
    syn match	cmudictPhoneArpabet	"\<A[AEHOWY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<E[HRY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<I[HY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<O[WY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<U[HWX][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[BDFGKLMNPQRSTVWYZ]\>"
    syn match	cmudictPhoneArpabet	"\<[CDHJSTZ]H\>"
    syn match	cmudictPhoneArpabet	"\<AXR\=0\=\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<IX0\=\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[DN]X\>"
    syn match	cmudictPhoneArpabet	"\<E[LMN]\>"
    syn match	cmudictPhoneArpabet	"\<E\=NG\>"
    syn match	cmudictPhoneArpabet	"\<H[VW]\>"
  elseif cmudict_phoneset == 'cepstral'
    syn match	cmudictPhoneArpabet	"\<a[aehowy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<e[hry][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<i[h]\=[0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<o[wy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<u[hw][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[bdfghjklmnprstvwz]\>"
    syn match	cmudictPhoneArpabet	"\<[cdjstz]h\>"
    syn match	cmudictPhoneArpabet	"\<ng\>"
  elseif cmudict_phoneset == 'cmu'
    syn match	cmudictPhoneArpabet	"\<A[AEHOWY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<E[HRY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<I[HY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<O[WY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<U[HW][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[BDFGKLMNPRSTVWYZ]\>"
    syn match	cmudictPhoneArpabet	"\<[CDHJSTZ]H\>"
    syn match	cmudictPhoneArpabet	"\<NG\>"
  elseif cmudict_phoneset == 'festvox'
    syn match	cmudictPhoneArpabet	"\<a[aehowy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<e[hry][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<i[hy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<o[wy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<u[hw][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[bdfgklmnprstvwyz]\>"
    syn match	cmudictPhoneArpabet	"\<[cdhjstz]h\>"
    syn match	cmudictPhoneArpabet	"\<ax0\=\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<ng\>"
  elseif cmudict_phoneset == 'timit'
    syn match	cmudictPhoneArpabet	"\<a[aehowy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<e[hry][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<i[hy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<o[wy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<u[hwx][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[bdfgklmnpqrstvwyz]\>"
    syn match	cmudictPhoneArpabet	"\<[cdhjstz]h\>"
    syn match	cmudictPhoneArpabet	"\<axr\=0\=\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<ix0\=\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[dn]x\>"
    syn match	cmudictPhoneArpabet	"\<e[lmn]\>"
    syn match	cmudictPhoneArpabet	"\<e\=ng\>"
    syn match	cmudictPhoneArpabet	"\<[pbtdkg]cl\>"
    syn match	cmudictPhoneArpabet	"\<h[vw]\>"
  endif
elseif cmudict_accent == 'en-GB-x-rp'
  if cmudict_phoneset == 'arpabet'
    syn match	cmudictPhoneArpabet	"\<A[AEHOWY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<E[AHRY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<I[AHY]\=[0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<O[AHWY][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<U[AHWX]\=[0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[BDFGKLMNPQRSTVWYZ]\>"
    syn match	cmudictPhoneArpabet	"\<[CDHJSTZ]H\>"
    syn match	cmudictPhoneArpabet	"\<AXR\=0\=\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<IX0\=\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[DN]X\>"
    syn match	cmudictPhoneArpabet	"\<E[LMN]\>"
    syn match	cmudictPhoneArpabet	"\<E\=NG\>"
    syn match	cmudictPhoneArpabet	"\<H[VW]\>"
  elseif cmudict_phoneset == 'cepstral'
    syn match	cmudictPhoneArpabet	"\<a[ehowy]\=[0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<e[@hry][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<i[@h]\=[0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<o[awy][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<u[hw][0-2]\>" contains=cmudictPhoneStress
    syn match	cmudictPhoneArpabet	"\<[bdfghjklmnprstvwz]\>"
    syn match	cmudictPhoneArpabet	"\<[cdjstz]h\>"
    syn match	cmudictPhoneArpabet	"\<ng\>"
  endif
endif

syn match	cmudictPhone		"\<[^ \t]\+\>" contains=cmudictPhoneArpabet

syn match	cmudictMetadataOperator	"="
syn match	cmudictMetadataKey	" [a-zA-Z0-9\_\-]\+=" contains=cmudictMetadataOperator

syn match	cmudictMetadataPreProc	"@@"
syn match	cmudictMetadata		"@@.\+@@" contains=cmudictMetadataPreProc,cmudictMetadataKey

syn match	cmudictVariant		"[^()]\+"
syn region	cmudictEntryVariant	start='(' end=')' contains=cmudictVariant

syn region	cmudictEntryComment	start='#' end='$' contains=cmudictMetadata

syn match	cmudictEntry		"^[^A-Za-z0-9]\=[^ \t(#]\+"

syn match	cmudictPronunciation	"  [^#]\+" contains=cmudictPhone

syn region	cmudictLineComment	start='^;;;' end='$' contains=cmudictMetadata
syn region	cmudictLineComment	start='^##' end='$' contains=cmudictMetadata

" Define the default highlighting.
" Only used when an item doesn't have highlighting yet
hi def link cmudictEntryComment		cmudictComment
hi def link cmudictLineComment		cmudictComment
hi def link cmudictComment		Comment
hi def link cmudictEntry		Identifier
hi def link cmudictEntryVariant		None
hi def link cmudictVariant		Constant
hi def link cmudictPhoneArpabet		None
hi def link cmudictPhoneStress		Constant
hi def link cmudictPhone		Error
hi def link cmudictMetadataOperator	None
hi def link cmudictMetadataPreProc	PreProc
hi def link cmudictMetadataKey		Type
hi def link cmudictMetadata		Constant
hi def link cmudictPhone		Error

let b:current_syntax = "cmudict"
" vim: ts=8
