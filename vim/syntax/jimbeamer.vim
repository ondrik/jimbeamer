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

" Four spaces of indent is not a listing in this format -- only a fence is
" -- so markdown's indented code block has to go, or an indented directive
" or raw LaTeX inside a list item is coloured as code and nothing of ours
" can reach inside the region to say otherwise.
syn clear markdownCodeBlock
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
      \ /^\s*\%((\%(\d\{1,9}\|[A-Za-z]\|[ivxlcdm]\{2,}\|[IVXLCDM]\{2,}\))\|\%([A-Za-z]\|[ivxlcdm]\{2,}\|[IVXLCDM]\{2,}\))\|\d\{1,9}[.)]\)\ze[ \t]/

" A thematic break starts an untitled frame.
syn match jimbeamerBreak /^\s\{0,3}\%(---\+\|\*\*\*\+\|___\+\)[ \t]*$/

syn match jimbeamerLatexMacro
      \ /\\[A-Za-z@]\+\*\=\%(\[[^]\n]*\]\)\=\%({[^{}]*}\)*/
      \ contains=jimbeamerMath

" The document's block is metadata only at the very start of the file and
" only when a closing fence follows; the converter applies the same rule, and
" without the fence this is an ordinary thematic break.
" A region cannot look ahead, so a '---' with no closing fence still opens
" this one -- and the converter, which can, calls that an ordinary thematic
" break.  A heading ends it, which is as far wrong as it can now go: without
" that it ran to the end of the file and painted the first heading as a YAML
" comment, since '#' starts one inside this region.
"
" A fence ends it for the same reason, and this is the first of six places
" below that say so.  The heading guard stopped the runaway at the next
" frame; between the opener and that heading a listing was still swallowed,
" so a deck whose front matter is missing its closing fence had its first
" listing coloured as YAML (issue #26).  The pattern is the opening line of
" jimbeamerCodeFence, both fence characters, and nothing else: a closer is
" one too, which costs nothing here, but a line that merely contains
" backticks is not, or '===' and '$$' and '\[' -- all of which legitimately
" hold text -- would end on their own contents.  'me=s-1' leaves the fence
" line itself free, which is what lets jimbeamerCodeFence, defined last and
" so preferred, take it.
syn region jimbeamerFrontMatter matchgroup=jimbeamerMetaFence
      \ start=/\%^---[ \t]*$/ end=/^\%(---\|\.\.\.\)[ \t]*$/
      \ end=/^\s*#\{1,6}\%([ \t]\|$\)/me=s-1
      \ end=/^\s*\%(`\{3,}[^`]*\|\~\{3,}.*\)$/me=s-1
      \ keepend contains=jimbeamerMetaKey,jimbeamerMetaComment,jimbeamerMetaString

" A slide's own block: '===' opens it, '---' closes it.  The asymmetry is the
" point -- '---' alone starts a slide, and only '===' opens a block.
" SLIDE_METADATA_RE wants a run of non-blank lines and then the closing
" fence, so a blank line means this was never a block -- and a heading is
" the frame boundary.  Both end it here, or a bare '===' swallowed the rest
" of the slide and repainted the next frame break as a fence.
" A fence ends it as well -- see jimbeamerFrontMatter above for the pattern
" -- and here the converter is explicit about it: a block's content may hold
" no code fence, so a fence line proves this was never a block.  Without it
" '===' with a listing under it coloured the listing as metadata.
syn region jimbeamerSlideMeta matchgroup=jimbeamerMetaFence
      \ start=/^===[ \t]*$/ end=/^\%(---\|\.\.\.\)[ \t]*$/
      \ end=/^\s*$/ end=/^\s*#\{1,6}\%([ \t]\|$\)/me=s-1
      \ end=/^\s*\%(`\{3,}[^`]*\|\~\{3,}.*\)$/me=s-1
      \ keepend contains=jimbeamerSlideKey,jimbeamerMetaKey,jimbeamerMetaComment,
      \ jimbeamerMetaString

syn match jimbeamerMetaKey /^\s*[A-Za-z][-A-Za-z0-9_]*\ze\s*:/ contained
" the keys a slide understands, told apart from one it will warn about
syn match jimbeamerSlideKey
      \ /^\s*\%(title\|label\|options\|itemsep\|part\|section\|subsection\|ifnot\|if\)\ze\s*:/
      \ contained
syn match jimbeamerMetaComment /#.*$/ contained
" '%' comments a metadata line too -- YAML has no comment this format could
" borrow there, so the converter takes such a line out before reading it.
" Anchored to the line, because a bare '%' inside a value is a per cent sign.
syn match jimbeamerMetaComment /^\s*%.*$/ contained
" and the one that came first: YAML_COMMENT_RE has taken an HTML comment out
" of a metadata block since before '%' did.
syn match jimbeamerMetaComment /^\s*<!--.\{-}-->[ \t]*$/ contained
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

syn match jimbeamerDirective /^\s*@[A-Za-z][-A-Za-z0-9_]*/
      \ nextgroup=jimbeamerDirectiveArgs
syn match jimbeamerDirectiveArgs /.*$/ contained
      \ contains=jimbeamerOverlay,jimbeamerMath,jimbeamerLatexMacro
syn match jimbeamerDirectiveEnd /^\s*@end\%([ \t]\+[A-Za-z][-A-Za-z0-9_]*\)\=[ \t]*$/
syn match jimbeamerOverlay /<[^>\n]*>/ contained

" '@preamble' is LaTeX for the preamble rather than an environment on a
" slide, and its contents are nobody's Markdown.  After the general
" directive match: where two items match in the same place vim prefers the
" one defined last, and this one has to win the opening line.
syn region jimbeamerPreamble matchgroup=jimbeamerDirective
      \ start=/^\s*@preamble[ \t]*$/
      \ end=/^\s*@end\%([ \t]\+preamble\)\=[ \t]*$/
      \ end=/^\s\{0,3}#\{1,6}\%([ \t]\|$\)/me=s-1
      \ keepend contains=jimbeamerLatexMacro,jimbeamerComment

" ---------------------------------------------------------------------------
" Raw LaTeX, which passthrough makes ordinary here
" ---------------------------------------------------------------------------

" Every environment ends at a heading as well, which is what
" RawLatexEnvironment.parse() does: without it an unterminated '\begin'
" swallowed the rest of the file, and a deck of twenty frames came out as
" one.  The syntax file did exactly what the converter was changed to stop
" doing.
syn region jimbeamerLatexEnv matchgroup=jimbeamerLatexMacro
      \ start=/^[ \t]*\\begin{\z([A-Za-z@*]\+\)}/
      \ end=/^[ \t]*\\end{\z1}/
      \ end=/^\s*#\{1,6}\%([ \t]\|$\)/me=s-1
      \ keepend contains=jimbeamerMath,jimbeamerMathDisplay,jimbeamerLatexMacro

" An environment whose contents are taken literally: a '# ' line in one is
" a shell or Python comment, not a heading, so only the matching \end closes
" it.  This is VERBATIM_ENVIRONMENTS, and it is listed last so that it wins
" -- of two regions that can start in the same place, vim takes the later.
syn region jimbeamerLatexEnv matchgroup=jimbeamerLatexMacro
      \ start=/^[ \t]*\\begin{\z(lstlisting\|verbatim\|Verbatim\|alltt\|minted\|semiverbatim\|comment\)}/
      \ end=/^[ \t]*\\end{\z1}/
      \ keepend contains=jimbeamerMath,jimbeamerMathDisplay,jimbeamerLatexMacro

" \pausex is the deck's pause, and the reason a deck has a macro line at all.
syn match jimbeamerPause /\\\%(pausex\|xpause\)\>/

" ---------------------------------------------------------------------------
" Maths: four spellings, none of whose contents are Markdown
" ---------------------------------------------------------------------------

" A fence ends it -- see jimbeamerFrontMatter for the pattern.  '$$' with no
" closing '$$' is the one of the six that reads most like ordinary prose,
" and it ran to the end of the file: a '$$' left behind by an edit swallowed
" the listing under it and coloured it as maths (issue #26).  Nothing else
" ends it, because display maths does hold text and a blank line is legal
" inside it.
syn region jimbeamerMathDisplay start=/\$\$/ end=/\$\$/ keepend
      \ end=/^\s*\%(`\{3,}[^`]*\|\~\{3,}.*\)$/me=s-1
      \ contains=jimbeamerLatexMacro
syn region jimbeamerMath start=/\$\ze[^$ \t]/ end=/\$/ oneline keepend
      \ contains=jimbeamerLatexMacro
" Display maths has the line to itself, as the converter requires: at most
" indentation before the opener and nothing
" but blanks after the closer.  Anchored, because '\[' is also Markdown's
" escape for a bracket -- unanchored, 'an interval \[0, 1)' opened a region
" that ran to the next '\]' anywhere in the file, colouring the headings
" and lists in between.
"
" The blank line is a second ending, because an opener whose closer never
" ends a line is not maths at all -- it is an escaped bracket, and the
" converter reads it inside one paragraph.  Without it such a line opens a
" region that runs to the end of the file.
" On one line: 'oneline' is what makes this follow the converter exactly.
" A region that finds no end on its line is not applied at all, so
" '\[0, 1) is an interval' -- an opener with nothing to close it -- is left
" as the prose it is, rather than opening something that runs away.
syn region jimbeamerMathBracket
      \ start=/^\s*\\\[/ end=/\\\]\ze[ \t]*$/ oneline keepend
      \ contains=jimbeamerLatexMacro

" Across lines, where the opener has its own line.  The blank line is a
" second ending: the converter reads this inside one paragraph, so an
" unclosed opener cannot reach past it.  An opener with content after it
" and its closer lines below ('\[ x =' ... 'y \]') is legal input and
" goes uncoloured, which is the price of not looking ahead.
" A fence is the third ending -- see jimbeamerFrontMatter for the pattern.
" The blank line only bounds the runaway at the paragraph; a '\[' with a
" listing directly under it, no blank line between, still ate the listing.
syn region jimbeamerMathBracket
      \ start=/^\s*\\\[[ \t]*$/ end=/\\\]\ze[ \t]*$/ end=/^\s*$/
      \ end=/^\s*\%(`\{3,}[^`]*\|\~\{3,}.*\)$/me=s-1
      \ keepend contains=jimbeamerLatexMacro
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
" '\]' inside, so a citation can go in one: '[\[Clarke 81\]]{.hlvio}'.
" Without the escape alternative the contents stop at the first ']' and the
" span is not a span at all.
syn match jimbeamerSpan /\[\%(\\.\|\_[^]]\)\{-}\]{[^}\n]*}/
      \ contains=jimbeamerSpanText,jimbeamerClass
syn match jimbeamerSpanText /\[\zs\_[^]]\{-}\ze\]/ contained

" An image with the attribute list jimbeamer reads.
syn match jimbeamerImage /!\[[^]\n]*\]([^)\n]*)\%({[^}\n]*}\)\=/
      \ contains=jimbeamerAttributes

" A code span, which markdown.vim also has and gets wrong in the one way
" that matters here: its region runs from a backtick to the next backtick
" anywhere in the file, so a run of three is closed by the first of them.
" A lone '`' in prose therefore swallowed the listing below it -- the
" fence's own line was already inside the region, and a region cannot start
" inside one that does not contain it, so jimbeamerCodeFence never got the
" chance to win (issue #26).  Clearing it is the same treatment
" markdownCodeBlock gets above, except that this one has to be replaced
" rather than merely dropped: a code span is still a code span here, and
" jimbeamerHeading has named this group since before it existed.
"
" What ours says instead is what the converter does.  A run of backticks is
" closed by a run of the same length -- CommonMark's rule, which is what
" makes '``a`b``' one span and what keeps '```' from closing '`' -- and a
" span lives inside one paragraph, so a blank line or a code fence ends it.
" It is not 'oneline': prose is wrapped, and 'some `code' / 'span` here'
" comes out as one span, the way jimbeamerSpan and jimbeamerHighlight do.
"
" Before jimbeamerCodeFence on purpose: a '```' with an info string holding
" no backtick is both a fence opener and the start of a span, and of two
" regions that can start in the same place vim takes the later.
"
" Cleared rather than left alongside, because the cleared one was still
" reachable through markdown's own @markdownInline cluster and still ran
" away from there: '[link `a](url)' with a listing below it painted the
" listing as code from inside the link's text.  Ours is deliberately not
" put into that cluster to take its place -- inside markdownLinkText
" nothing but the cluster can start, so a span there would beat
" jimbeamerCodeFence on the fence line and the listing would be swallowed
" again.  The price is that a code span inside a link's text is no longer
" told apart from the link text around it, which is colour and not
" correctness.
syn clear markdownCode
syn region jimbeamerInlineCode matchgroup=jimbeamerCodeDelim keepend
      \ start=/\z(`\+\)/ end=/`\@<!\z1`\@!/
      \ end=/^\s*$/ end=/^\s*\%(`\{3,}[^`]*\|\~\{3,}.*\)$/me=s-1

" ---------------------------------------------------------------------------
" Comments
" ---------------------------------------------------------------------------

" A '%' is a comment only as the first thing on its line; part-way along one
" it is passed through to LaTeX, where it comments out the rest of the line.
syn match jimbeamerComment /^[ \t]*%.*$/

" '<!--' is two things, the way '\[' is, and the line decides which.
"
" Part-way along a line it is inline HTML inside a paragraph: the converter
" drops it and keeps the prose either side, and the paragraph is as far as
" it reaches.  So a blank line ends it, and so does a code fence -- a fence
" interrupts a paragraph, which is the case issue #26 reports: 'a <!--'
" with a listing directly under it coloured the listing as a comment, and
" without a blank line anywhere below, the rest of the deck with it.
syn region jimbeamerHtmlComment start=/<!--/ end=/-->/ keepend
      \ end=/^\s*$/ end=/^\s*\%(`\{3,}[^`]*\|\~\{3,}.*\)$/me=s-1

" Beginning a line it is an HTML block instead, and the converter removes
" the block whole: a listing commented out inside one is comment and not a
" listing, so no fence may end this and the region runs to '-->' alone.
" Unterminated it reaches the end of the file -- which is what the
" converter does with it too, so for once the runaway is the right colour.
" Last of the two, so that it wins the line it begins.
syn region jimbeamerHtmlComment start=/^\s*<!--/ end=/-->/ keepend

" ---------------------------------------------------------------------------
" Code fences, so that a '%' or a '@' inside one is not mistaken for ours
" ---------------------------------------------------------------------------

" Two regions rather than one, split on the fence character, because a
" closer may be longer than its opener -- the converter closes '```' on
" '`````' -- and one region cannot say "more of whatever \z1 was made of"
" without also letting tildes close a backtick fence.
"
" \z1 is the opener's indent and \z2 its run of fence characters.  The
" converter closes on a fence indented up to three columns past its opener,
" and a region cannot measure that, so it is written as the two cases that
" can be:
"
"   ^\z1 \{0,3}      the opener's own indent, and up to three columns more
"   ^ \{0,3}         three columns or fewer from the margin
"
" The second needs no reference to the opener: an indent of three or less is
" within "opener plus three" whatever the opener was, since no indent is
" negative.  So it is exact rather than a guess.
"
" Three *spaces* in both, not three \s: a tab is four columns and so is
" already past the allowance, but it is one character, and counting it as
" one is how a tab-indented fence quoted inside a listing used to end the
" listing.
"
" The info string of a backtick fence may not hold a backtick -- CommonMark's
" rule, and marko's -- so '```a``` b' is a paragraph, not a fence.  Anchoring
" the start at the end of the line is what enforces it.
"
" Known gap: a closer indented LESS than its opener, by more than three
" columns from the margin, leaves the region open where the converter closes
" it -- an opener eight columns in and a closer at six, say.  So does a
" closer indented with different whitespace characters than its opener, a tab
" against four spaces.  Neither is expressible: the two cases above are the
" most a region that compares indents as text rather than as columns can say.
" Both need the two ends of one fence to disagree about their indent, and the
" colour then goes wrong at the fence rather than halfway down the deck.
" '[ \t\d12]' rather than '[ \t]': a form feed is decimal 12, and marko turns
" one into a newline before any block parser runs, so the converter closes a
" fence at '```<FF>'.  Vim collections do not translate '\f', hence the
" decimal -- spelled '\f' it would match a backslash or an 'f', and '```f'
" would end a listing.
"
" A fence opened on a list marker's own line ('- ```') is NOT matched, and
" the attempt is recorded here because it looks easy and is not.  Letting an
" optional marker in front of the backticks colours that listing, and buys
" three new ways to open a region the converter never opens: a marker four
" columns in is prose here, an ordered marker other than '1.' cannot
" interrupt a paragraph and so is prose too -- neither of which a region can
" tell, the second needing to know what the previous line was -- and the six
" 'a fence ends it' patterns above would each need the marker as well, or a
" runaway region swallows the opener and the closer starts a fresh one.  A
" listing that goes uncoloured is a smaller fault than a region that runs to
" the end of the deck, so the marker stays out.
"
" Exotic whitespace after the backticks -- a no-break space, an en quad --
" used to close a fence for the converter and not here; CLOSE_RE says
" '[ \t]*$' now, as these do (issue #26, group B).
syn region jimbeamerCodeFence matchgroup=jimbeamerCodeDelim keepend
      \ start=/^\z(\s*\)\z(`\{3,}\)[^`]*$/
      \ end=/^\z1 \{0,3}\z2`*[ \t\d12]*$/
      \ end=/^ \{0,3}\z2`*[ \t\d12]*$/
syn region jimbeamerCodeFence matchgroup=jimbeamerCodeDelim keepend
      \ start=/^\z(\s*\)\z(\~\{3,}\).*$/
      \ end=/^\z1 \{0,3}\z2\~*[ \t\d12]*$/
      \ end=/^ \{0,3}\z2\~*[ \t\d12]*$/

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
hi def link jimbeamerInlineCode       String

" Both metadata blocks, the environments and the wrapped inline spans can
" all start well above the window, so looking back a little is necessary.
syn sync minlines=60

let b:current_syntax = 'jimbeamer'
