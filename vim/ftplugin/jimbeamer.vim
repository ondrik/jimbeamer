" Filetype settings for jimbeamer.
"
" What this is for: a deck is an ordinary '.md' file, so vim loads its
" markdown ftplugin first and that sets 'commentstring' to '<!--%s-->'.
" ftdetect then switches the filetype to ours, and without this file the
" buffer keeps whatever markdown left behind -- which is why 'gcc' and
" every other comment plugin wrapped a line in HTML comments.
"
" A '%' line is the comment this format has: the converter removes it
" before anything parses the document, so it never reaches the .tex.
" '<!-- ... -->' is dropped too, but it is an HTML *block*, and one
" between two list items splits the list in two.  A '%' line does not,
" which is what makes it the one to offer by default.
"
" It is also one-sided, so there is no closing half for a plugin to
" forget.

if exists('b:did_ftplugin')
  finish
endif
let b:did_ftplugin = 1

" '% %s', with the space, so 'gcc' gives '% text' rather than '%text'.
setlocal commentstring=%\ %s

" No blank required after the '%', since the converter does not require
" one either: a line of bare '%' is a comment as much as '% note' is.
setlocal comments=:%

" What 'gq' does to a paragraph.  Indentation carries meaning in a deck --
" a directive or a fence lined up under a bullet belongs to that item -- and
" re-wrapping without these flattens exactly the alignment that says so.
"
" 'n' makes a numbered list keep its hanging indent, and formatlistpat says
" what a marker looks like here: this format counts '(a)', 'a)', '(iv)' and
" '2.' as well as the bullets vim already knows.
setlocal formatoptions+=n
let &l:formatlistpat =
      \ '^\s*\%(\d\+[.)]\|(\=\%(\d\+\|\a\|[ivxlcdm]\+\|[IVXLCDM]\+\))\|[-*+]\)\s\+'

let b:undo_ftplugin =
      \ 'setlocal commentstring< comments< formatoptions< formatlistpat<'
