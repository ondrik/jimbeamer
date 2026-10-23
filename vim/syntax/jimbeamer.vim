" Vim syntax file
" Language:     jimbeamer -- Markdown for LaTeX Beamer slides
" Maintainer:   see the repository this ships with
"
" Markdown with the constructs jimbeamer adds to it, and with the raw LaTeX
" that its passthrough rule makes ordinary rather than exceptional: maths,
" macros and environments are content here, not an escape hatch, so they are
" highlighted as such.
"
" Loaded on top of the stock markdown syntax, so lists, emphasis, code fences
" and the rest keep working and only the differences are described here.

if exists('b:current_syntax')
  finish
endif

runtime! syntax/markdown.vim
unlet! b:current_syntax

syntax case match

" ---------------------------------------------------------------------------
" Metadata: the document's block, and a slide's own
" ---------------------------------------------------------------------------

" These two come first on purpose.  Where two items match at the same place
" vim prefers the one defined last, so everything below that has to beat a
" bare '---' or a bare '\macro' -- the metadata fences, the environments --
" must be defined after them.

" An ordered list's marker, which says what the list looks like: a letter
" or a roman numeral needs a parenthesis, a digit keeps CommonMark's '1.'.
syn match jimbeamerListMarker
      \ /^\s\{0,3}\%((\%(\d\{1,9}\|[A-Za-z]\|[ivxlcdm]\{2,}\|[IVXLCDM]\{2,}\))\|\%([A-Za-z]\|[ivxlcdm]\{2,}\|[IVXLCDM]\{2,}\))\|\d\{1,9}[.)]\)\ze[ \t]/

" A thematic break starts an untitled frame.
syn match jimbeamerBreak /^\s\{0,3}\%(---\+\|\*\*\*\+\|___\+\)[ \t]*$/

syn match jimbeamerLatexMacro
      \ /\\[A-Za-z@]\+\*\=\%(\[[^]\n]*\]\)\=\%({[^{}]*}\)*/
      \ contains=jimbeamerMath

" The document's block is metadata only at the very start of the file and
" only when a closing fence follows; the converter applies the same rule, and
" without the fence this is an ordinary thematic break.
syn region jimbeamerFrontMatter matchgroup=jimbeamerMetaFence
      \ start=/\%^---[ \t]*$/ end=/^\%(---\|\.\.\.\)[ \t]*$/
      \ keepend contains=jimbeamerMetaKey,jimbeamerMetaComment,jimbeamerMetaString

" A slide's own block: '===' opens it, '---' closes it.  The asymmetry is the
" point -- '---' alone starts a slide, and only '===' opens a block.
syn region jimbeamerSlideMeta matchgroup=jimbeamerMetaFence
      \ start=/^===[ \t]*$/ end=/^\%(---\|\.\.\.\)[ \t]*$/
      \ keepend contains=jimbeamerSlideKey,jimbeamerMetaKey,jimbeamerMetaComment,
      \ jimbeamerMetaString

syn match jimbeamerMetaKey /^\s*[A-Za-z][-A-Za-z0-9_]*\ze\s*:/ contained
" the keys a slide understands, told apart from one it will warn about
syn match jimbeamerSlideKey
      \ /^\s*\%(title\|label\|options\|itemsep\|part\|section\|subsection\)\ze\s*:/
      \ contained
syn match jimbeamerMetaComment /#.*$/ contained
syn region jimbeamerMetaString start=/'/ skip=/''/ end=/'/ oneline contained
syn region jimbeamerMetaString start=/"/ skip=/\\"/ end=/"/ oneline contained

" ---------------------------------------------------------------------------
" Slides
" ---------------------------------------------------------------------------

" A heading, with the attribute list jimbeamer reads off the end of it.
syn match jimbeamerHeading /^\s\{0,3}#\{1,6}\%([ \t].*\)\=$/
      \ contains=jimbeamerAttributes,jimbeamerMath,jimbeamerMathParen,
      \ jimbeamerInlineCode,jimbeamerHighlight,jimbeamerLatexMacro

syn match jimbeamerAttributes /{[^}]*}[ \t]*$/ contained
      \ contains=jimbeamerClass,jimbeamerLabel,jimbeamerOption
syn match jimbeamerClass /\.[A-Za-z@][-A-Za-z0-9_@]*/ contained
syn match jimbeamerLabel /#[A-Za-z][-A-Za-z0-9_]*/ contained
syn match jimbeamerOption /[A-Za-z][-A-Za-z0-9_]*=[^ \t}]*/ contained

" ---------------------------------------------------------------------------
" Directives: '@name arguments' to '@end'
" ---------------------------------------------------------------------------

syn match jimbeamerDirective /^\s\{0,3}@[A-Za-z][-A-Za-z0-9_]*/
      \ nextgroup=jimbeamerDirectiveArgs
syn match jimbeamerDirectiveArgs /.*$/ contained
      \ contains=jimbeamerOverlay,jimbeamerMath,jimbeamerLatexMacro
syn match jimbeamerDirectiveEnd /^\s\{0,3}@end\%([ \t]\+[A-Za-z][-A-Za-z0-9_]*\)\=[ \t]*$/
syn match jimbeamerOverlay /<[^>\n]*>/ contained

" '@preamble' is LaTeX for the preamble rather than an environment on a
" slide, and its contents are nobody's Markdown.  After the general
" directive match: where two items match in the same place vim prefers the
" one defined last, and this one has to win the opening line.
syn region jimbeamerPreamble matchgroup=jimbeamerDirective
      \ start=/^\s\{0,3}@preamble[ \t]*$/
      \ end=/^\s\{0,3}@end\%([ \t]\+preamble\)\=[ \t]*$/
      \ end=/^\s\{0,3}#\{1,6}\%([ \t]\|$\)/me=s-1
      \ keepend contains=jimbeamerLatexMacro,jimbeamerComment

" ---------------------------------------------------------------------------
" Raw LaTeX, which passthrough makes ordinary here
" ---------------------------------------------------------------------------

" An environment written out by hand is taken verbatim to its matching \end,
" so nothing inside it is Markdown.
syn region jimbeamerLatexEnv matchgroup=jimbeamerLatexMacro
      \ start=/^[ \t]*\\begin{\z([A-Za-z@*]\+\)}/
      \ end=/^[ \t]*\\end{\z1}/
      \ keepend contains=jimbeamerMath,jimbeamerMathDisplay,jimbeamerLatexMacro

" \pausex is the deck's pause, and the reason a deck has a macro line at all.
syn match jimbeamerPause /\\\%(pausex\|xpause\)\>/

" ---------------------------------------------------------------------------
" Maths: four spellings, none of whose contents are Markdown
" ---------------------------------------------------------------------------

syn region jimbeamerMathDisplay start=/\$\$/ end=/\$\$/ keepend
      \ contains=jimbeamerLatexMacro
syn region jimbeamerMath start=/\$\ze[^$ \t]/ end=/\$/ oneline keepend
      \ contains=jimbeamerLatexMacro
syn region jimbeamerMathBracket start=/\\\[/ end=/\\\]/ keepend
      \ contains=jimbeamerLatexMacro
syn region jimbeamerMathParen start=/\\(/ end=/\\)/ oneline keepend
      \ contains=jimbeamerLatexMacro

" ---------------------------------------------------------------------------
" Inline: the spans jimbeamer adds
" ---------------------------------------------------------------------------

" ==like this== becomes the highlight macro.  Three or more '=' are left
" alone, which is what keeps a setext underline safe.
" The contents may cross a line break, since prose is wrapped.
syn match jimbeamerHighlight
      \ /\%(=\)\@<!==[^= \t]\_[^=]\{-}[^= \t]==\%(=\)\@!/
syn match jimbeamerHighlight /\%(=\)\@<!==[^= \t]==\%(=\)\@!/

" [text]{.macro}: the class is the macro name.
" As the highlight, the text may wrap; the ']' and the '{' stay adjacent.
syn match jimbeamerSpan /\[\_[^]]\{-}\]{[^}\n]*}/
      \ contains=jimbeamerSpanText,jimbeamerClass
syn match jimbeamerSpanText /\[\zs\_[^]]\{-}\ze\]/ contained

" An image with the attribute list jimbeamer reads.
syn match jimbeamerImage /!\[[^]\n]*\]([^)\n]*)\%({[^}\n]*}\)\=/
      \ contains=jimbeamerAttributes

" ---------------------------------------------------------------------------
" Comments
" ---------------------------------------------------------------------------

" A '%' is a comment only as the first thing on its line; part-way along one
" it is passed through to LaTeX, where it comments out the rest of the line.
syn match jimbeamerComment /^[ \t]*%.*$/
syn region jimbeamerHtmlComment start=/<!--/ end=/-->/ keepend

" ---------------------------------------------------------------------------
" Code fences, so that a '%' or a '@' inside one is not mistaken for ours
" ---------------------------------------------------------------------------

syn region jimbeamerCodeFence matchgroup=jimbeamerCodeDelim
      \ start=/^\s\{0,3}\z(`\{3,}\|\~\{3,}\)\s*\%([A-Za-z0-9_+-]*\)/
      \ end=/^\s\{0,3}\z1\s*$/ keepend

" ---------------------------------------------------------------------------

hi def link jimbeamerMetaFence        PreProc
hi def link jimbeamerCodeFence        String
hi def link jimbeamerCodeDelim        PreProc
hi def link jimbeamerMetaKey          Identifier
hi def link jimbeamerSlideKey         Statement
hi def link jimbeamerMetaComment      Comment
hi def link jimbeamerMetaString       String
hi def link jimbeamerHeading          Title
hi def link jimbeamerAttributes       Special
hi def link jimbeamerClass            Type
hi def link jimbeamerLabel            Underlined
hi def link jimbeamerOption           Special
hi def link jimbeamerBreak            PreProc
hi def link jimbeamerListMarker       Identifier
hi def link jimbeamerDirective        Statement
hi def link jimbeamerPreamble        String
hi def link jimbeamerDirectiveEnd     Statement
hi def link jimbeamerDirectiveArgs    Normal
hi def link jimbeamerOverlay          Special
hi def link jimbeamerLatexEnv         String
hi def link jimbeamerLatexMacro       Function
hi def link jimbeamerPause            Todo
hi def link jimbeamerMath             Number
hi def link jimbeamerMathDisplay      Number
hi def link jimbeamerMathBracket      Number
hi def link jimbeamerMathParen        Number
hi def link jimbeamerHighlight        Special
hi def link jimbeamerSpan             Type
hi def link jimbeamerSpanText         Normal
hi def link jimbeamerImage            Underlined
hi def link jimbeamerComment          Comment
hi def link jimbeamerHtmlComment      Comment

" Both metadata blocks, the environments and the wrapped inline spans can
" all start well above the window, so looking back a little is necessary.
syn sync minlines=60

let b:current_syntax = 'jimbeamer'
