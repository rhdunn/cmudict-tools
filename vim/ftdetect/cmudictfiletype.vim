" Cached versions of the global values to preserve user settings.
let s:current_fileformats   = ''
let s:current_fileencodings = ''

function! s:detect_cmudict(line)
  if !exists("b:cmudictsyntax")
    let text = getline(a:line)
    if !match(text, '^;;; # CMUdict  --  Major Version: ')
      let b:cmudictsyntax = "cmudict"
    elseif !match(text, '^## The Carnegie Mellon Pronouncing Dictionary ')
      let b:cmudictsyntax = "cmudict"
      let b:cmudict_format = "cmudict-weide"
    elseif !match(text, '^A  AH0$')
      let b:cmudictsyntax = "cmudict"
    elseif !match(text, '^!EXCLAMATION-POINT  EH2 K S K L AH0 M EY1 SH AH0 N P OY2 N T$')
      let b:cmudictsyntax = "cmudict"
    endif
  endif
endfunction

function! s:filetype_cmudict(mode)
  if !exists("b:cmudictsyntax")
    call s:detect_cmudict(1)
    call s:detect_cmudict(2)
    call s:detect_cmudict(3)
    call s:detect_cmudict(4)
    call s:detect_cmudict(5)
  endif

  if exists("b:cmudictsyntax")
    if a:mode == "pre"
      let s:current_fileformats   = &g:fileformats
      let s:current_fileencodings = &g:fileencodings
      set fileencodings=windows-1252 fileformats=unix
      setlocal filetype=cmudict
    elseif a:mode == "post"
      let &g:fileformats   = s:current_fileformats
      let &g:fileencodings = s:current_fileencodings
    endif
  endif
endfunction

au BufRead     cmudict* call s:filetype_cmudict("pre")
au BufReadPost cmudict* call s:filetype_cmudict("post")

au BufRead     acronym* call s:filetype_cmudict("pre")
au BufReadPost acronym* call s:filetype_cmudict("post")
