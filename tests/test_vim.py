"""The vim syntax file in vim/.

Nothing else in the suite looks at it, so it had already drifted behind the
format twice before this existed.  What is checked is what vim actually makes
of a deck: the file is loaded, a document is opened under it, and synID() is
asked which group every character ended up in.  Reading the patterns proves
nothing -- ordering alone decides most of what a vim syntax file does.

Skipped where vim is absent, so the suite still needs nothing but pytest.
"""

import io
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

VIM = shutil.which('vim')
vim_needed = pytest.mark.skipif(VIM is None, reason='vim is not installed')

HERE = os.path.dirname(os.path.abspath(__file__))
VIM_DIR = os.path.join(os.path.dirname(HERE), 'vim')


# A line for every construct the syntax file claims to know, so that one
# probe covers the lot.  Kept here rather than in conftest's EXAMPLE because
# these assertions are about colour, not about conversion.
SAMPLE = """\
---
title: 'How to Give a Talk'
---

# A heading {.fragile #intro}

* a bullet with $x_1 \\land y_2$
% a comment line
\\pausex

===
title: A slide
nosuchkey: 1
---

@preamble
\\usepackage{tikz}
% a preamble comment
@end preamble

@columns
@column 0.45
```C
int main(void) { return 0; }
```
@end

\\begin{tabularx}{\\textwidth}{lX}
  pandoc & the obvious alternative \\\\
\\end{tabularx}

---

\\[
\\bigvee_i a_i
\\]

$$
\\sum_i x_i
$$

inline \\(x_3\\) and a citation \\[Clarke 81\\] mid-sentence

\\[0, 1) is an interval, not an opener

(a) a lettered item
(ii) a roman one
2. a plain one starting at two

* an item, with everything below lined up under it
    ```C
    int indented;
    ```
    @preamble
    \\usepackage{tikz}
    plain words in a preamble
    @end preamble
    @minipage 6cm
    \\input{figs/x}
    @end minipage
  * nested
    (a) lettered under a nested bullet

    \\[
      x^2
    \\]

a citation [\\[Clarke 81\\]]{.hlvio} inside a span

==highlighted== and [red]{.hlrd}

a `code span`, ``one with a ` inside`` and one that `wraps over
the line break` too

a span that [wraps across
a line]{.hlgr}, and ==a highlight
that wraps== too

![A caption](f.png){width=0.4}
"""

PROSE = """\
# Prose

A. Turing wrote about machines
i.e. this is prose
Note. a sentence
"""

PROBE = """\
set nocompatible
set runtimepath^=%(runtimepath)s
syntax enable
set filetype=%(filetype)s
let s:out = []
for s:l in range(1, line('$'))
  let s:groups = []
  let s:line = getline(s:l)
  let s:c = 1
  while s:c <= strlen(s:line)
    let s:g = synIDattr(synID(s:l, s:c, 1), 'name')
    if s:g !=# '' && (empty(s:groups) || s:groups[-1] !=# s:g)
      call add(s:groups, s:g)
    endif
    let s:c += 1
  endwhile
  call add(s:out, [s:line, s:groups])
endfor
call writefile([json_encode(s:out)], '%(out)s')
qall!
"""


def run_vim(tmp_path, text, filetype='jimbeamer'):
    """run_vim(Path, str, str) -> [(str, [str])]

Opens `text' in vim under the syntax file and returns, for each line, the
syntax groups its characters fell into, in the order they appear.
"""
    source = tmp_path / 'deck.md'
    source.write_text(text, encoding='utf-8')
    out = tmp_path / 'groups.json'
    script = tmp_path / 'probe.vim'
    script.write_text(PROBE % {'runtimepath': VIM_DIR, 'filetype': filetype,
                               'out': str(out)}, encoding='utf-8')

    subprocess.run([VIM, '-N', '-u', 'NONE', '-i', 'NONE',
                    '-S', str(script), str(source)],
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=60, check=False)

    assert out.exists(), 'vim wrote no result; the syntax file may not load'
    return [(line, groups)
            for line, groups in json.loads(out.read_text(encoding='utf-8'))]


def groups_on(probed, needle):
    """groups_on([(str, [str])], str) -> [str]: the line holding `needle'.

A needle ending in a newline has to be the whole line, which is how '@end'
is told from '@end preamble'.
"""
    for line, groups in probed:
        if needle.endswith('\n'):
            if line.strip() == needle.strip():
                return groups
        elif needle in line:
            return groups
    raise AssertionError('no line holding %r' % needle)


@pytest.fixture(scope='module')
def sample(tmp_path_factory):
    if VIM is None:
        pytest.skip('vim is not installed')
    return run_vim(tmp_path_factory.mktemp('sample'), SAMPLE)


@pytest.fixture(scope='module')
def prose(tmp_path_factory):
    if VIM is None:
        pytest.skip('vim is not installed')
    return run_vim(tmp_path_factory.mktemp('prose'), PROSE)


@pytest.fixture(scope='module')
def example(tmp_path_factory):
    """conftest.EXAMPLE, which grows as the format does."""
    if VIM is None:
        pytest.skip('vim is not installed')
    sys.path.insert(0, HERE)
    import conftest

    return run_vim(tmp_path_factory.mktemp('example'), conftest.EXAMPLE)


###########################################
# the constructs the file claims to know
###########################################

@vim_needed
@pytest.mark.parametrize('needle, group', [
    pytest.param("title: 'How to Give a Talk'", 'jimbeamerMetaKey', id='meta'),
    pytest.param('# A heading', 'jimbeamerHeading', id='heading'),
    pytest.param('{.fragile #intro}', 'jimbeamerClass', id='class'),
    pytest.param('{.fragile #intro}', 'jimbeamerLabel', id='label'),
    pytest.param('% a comment line', 'jimbeamerComment', id='comment'),
    pytest.param('\\pausex', 'jimbeamerPause', id='pause'),
    pytest.param('title: A slide', 'jimbeamerSlideKey', id='slide-key'),
    pytest.param('nosuchkey: 1', 'jimbeamerMetaKey', id='unknown-slide-key'),
    pytest.param('@columns', 'jimbeamerDirective', id='directive'),
    pytest.param('@preamble', 'jimbeamerDirective', id='preamble-open'),
    pytest.param('@end preamble', 'jimbeamerDirective', id='preamble-end'),
    # the body is LaTeX, not Markdown: it was markdownEscape before
    pytest.param('\\usepackage{tikz}', 'jimbeamerLatexMacro', id='preamble'),
    pytest.param('% a preamble comment', 'jimbeamerComment', id='preamble-%'),
    pytest.param('@end\n', 'jimbeamerDirectiveEnd', id='directive-end'),
    pytest.param('int main(void)', 'jimbeamerCodeFence', id='code-fence'),
    pytest.param('pandoc & the obvious', 'jimbeamerLatexEnv', id='latex-env'),
    pytest.param('$x_1 \\land y_2$', 'jimbeamerMath', id='maths'),
    pytest.param('\\bigvee_i a_i', 'jimbeamerMathBracket', id='display-maths'),
    pytest.param('\\sum_i x_i', 'jimbeamerMathDisplay', id='dollar-maths'),
    pytest.param('a `code span`', 'jimbeamerInlineCode', id='code-span'),
    pytest.param('``one with a ` inside``', 'jimbeamerInlineCode',
                 id='code-span-holding-a-backtick'),
    pytest.param('\\(x_3\\)', 'jimbeamerMathParen', id='latex-inline-maths'),
    pytest.param('(a) a lettered', 'jimbeamerListMarker', id='lettered'),
    pytest.param('(ii) a roman', 'jimbeamerListMarker', id='roman'),
    pytest.param('2. a plain one', 'jimbeamerListMarker', id='plain-ordered'),
    pytest.param('==highlighted==', 'jimbeamerHighlight', id='highlight'),
    pytest.param('[red]{.hlrd}', 'jimbeamerSpan', id='span'),
    pytest.param('![A caption]', 'jimbeamerImage', id='image'),
])
def test_the_construct_is_coloured(sample, needle, group):
    assert group in groups_on(sample, needle), \
        'expected %s on the line holding %r' % (group, needle)


@vim_needed
def test_a_slide_key_it_knows_is_told_from_one_it_does_not(sample):
    """So a typo is visible before the converter warns about it."""
    assert 'jimbeamerSlideKey' in groups_on(sample, 'title: A slide')
    assert 'jimbeamerSlideKey' not in groups_on(sample, 'nosuchkey: 1')


@vim_needed
@pytest.mark.parametrize('needle, group', [
    pytest.param('a span that [wraps across', 'jimbeamerSpan', id='span'),
    pytest.param('that wraps== too', 'jimbeamerHighlight', id='highlight'),
    pytest.param('the line break`', 'jimbeamerInlineCode', id='code-span'),
])
def test_an_inline_span_may_wrap(sample, needle, group):
    """Prose is wrapped, and the converter reads these across a line break.
The editor showing them as broken text is the same bug seen from the other
side."""
    assert group in groups_on(sample, needle)


@vim_needed
def test_a_lone_break_is_a_break_and_a_fence_is_a_fence(sample):
    """The '---' that closes a slide's metadata and the one that starts an
untitled frame are the same characters, and must not be the same colour."""
    assert groups_on(sample, '---')[0] == 'jimbeamerMetaFence'
    lone = [groups for line, groups in sample
            if line.strip() == '---' and groups == ['jimbeamerBreak']]
    assert lone, 'expected a thematic break somewhere'


###########################################
# what it must leave alone
###########################################

@vim_needed
@pytest.mark.parametrize('needle', [
    pytest.param('a citation', id='mid-sentence'),
    pytest.param('is an interval', id='opens-the-line'),
])
def test_an_escaped_bracket_is_not_display_maths(sample, needle):
    """The converter reads '\\[' as display maths only where it has the
line to itself; anywhere else it is Markdown's escape for a bracket.  The
syntax file used to open a region at any '\\[' and, not being oneline,
run it to the next '\\]' -- which coloured the headings and lists of the
rest of the file as maths."""
    assert 'jimbeamerMathBracket' not in groups_on(sample, needle)


@vim_needed
def test_an_unclosed_bracket_stops_at_the_paragraph(sample):
    """'\\[0, 1) is an interval' opens nothing that can close, so the
region is ended by the blank line below it rather than by the end of the
file.  The list after it is a list again."""
    assert 'jimbeamerMathBracket' not in groups_on(sample, '(a) a lettered')
    assert 'jimbeamerMathBracket' not in groups_on(sample, '==highlighted==')


@vim_needed
@pytest.mark.parametrize('needle', [
    pytest.param('A. Turing', id='initial'),
    pytest.param('i.e. this is prose', id='ie'),
    pytest.param('Note. a sentence', id='word'),
])
def test_a_letter_and_a_full_stop_is_not_a_list(prose, needle):
    """The converter needs a parenthesis for a letter, and so does this."""
    assert 'jimbeamerListMarker' not in groups_on(prose, needle)


@vim_needed
def test_the_example_deck_has_nothing_vim_calls_an_error(example):
    """conftest.EXAMPLE grows as the format does, and stock markdown.vim
flags what it does not understand -- a raw LaTeX environment above all.  So
this fails when a construct is added to the format and not to the syntax
file, which is how it drifted behind twice before."""
    bad = [(line, groups) for line, groups in example
           if any('Error' in group for group in groups)]
    assert not bad, 'vim flags an error on: %r' % (bad[:3],)


@vim_needed
@pytest.mark.parametrize('needle, group', [
    pytest.param('int indented', 'jimbeamerCodeFence', id='fence'),
    pytest.param('plain words in a preamble', 'jimbeamerPreamble',
                 id='preamble-body'),
    pytest.param('(a) lettered under', 'jimbeamerListMarker', id='nested-marker'),
    pytest.param('x^2', 'jimbeamerMathBracket', id='display-maths'),
])
def test_an_indented_construct_is_still_itself(sample, needle, group):
    """Indentation stopped being syntax, and the converter measures what
is left relative to the list item.  Five rules here kept an absolute cap
of three spaces, which is one less than the ordinary indent of content
under a second-level bullet -- so a fence, a preamble, display maths and
a lettered marker all lost their colour exactly where a deck puts them."""
    assert group in groups_on(sample, needle)


@vim_needed
def test_a_span_may_hold_an_escaped_bracket(sample):
    """'[\\[Clarke 81\\]]{.hlvio}' is how a citation goes in one.  The
contents stopped at the first ']', so the span was not a span."""
    assert 'jimbeamerSpan' in groups_on(sample, 'inside a span')


@vim_needed
@pytest.mark.parametrize('opener, needle', [
    pytest.param('---\nnot: frontmatter, no fence\n', '# After', id='frontmatter'),
    pytest.param('# S\n\n===\n\nprose under a bare ===\n', '# After',
                 id='slide-block'),
    pytest.param('# S\n\n\\begin{tabularx}{\\textwidth}{lX}\n  a & b \\\\\n',
                 '# After', id='unclosed-environment'),
])
def test_a_region_whose_terminator_never_comes_stops(tmp_path, opener, needle):
    """A region cannot look ahead, so each of these still opens one -- and
each used to paint the rest of the file.  The converter stops at a
heading or declines the construct entirely; a heading ends them here.
The frontmatter one was the worst: '#' is a comment inside that region,
so the first heading of the deck came out greyed."""
    probed = run_vim(tmp_path, opener + '\n# After\n\n* a list\n')
    assert 'jimbeamerHeading' in groups_on(probed, needle)
    assert 'markdownListMarker' in groups_on(probed, '* a list')


@vim_needed
@pytest.mark.parametrize('opener', [
    pytest.param('---\ntitle: T\n', id='frontmatter'),
    pytest.param('`\n', id='code-span'),
    pytest.param('$$\n', id='dollar-maths'),
    pytest.param('===\n', id='slide-block'),
    pytest.param('\\[\n', id='escaped-bracket'),
    pytest.param('a <!--\n', id='html-comment'),
])
def test_a_fence_under_an_unterminated_region_is_still_a_listing(tmp_path,
                                                                 opener):
    """Issue #26, and the other half of the one above: a heading ends each
of these, so the runaway stopped at the next frame -- but between the
opener and that heading a listing was still swallowed, and came out
coloured as YAML, as maths or as a comment.  The converter makes every one
of these decks an lstlisting, so a fence ends them here as well.

A fence rather than any line holding backticks, because '===' and '$$' and
'\\[' all legitimately hold text, and ending them on their own contents is
the regression this guards."""
    probed = run_vim(tmp_path, opener + '```C\nint body;\n```\n')
    assert 'jimbeamerCodeFence' in groups_on(probed, 'int body;')


@vim_needed
def test_a_tilde_fence_stops_them_too(tmp_path):
    """The guard names both fence characters, since both open a listing.
Only the backtick half was reported, and only the backtick half would have
been noticed."""
    probed = run_vim(tmp_path, '$$\n~~~C\nint body;\n~~~\n')
    assert 'jimbeamerCodeFence' in groups_on(probed, 'int body;')


@vim_needed
@pytest.mark.parametrize('deck, needle, group', [
    pytest.param('# S\n\n===\nlabel: three ``` in a value\ntitle: T\n'
                 '---\n\nx\n',
                 'title: T', 'jimbeamerSlideMeta', id='slide-block'),
    pytest.param('# S\n\n$$\nx = a ``` b\n\\sum_i y\n$$\n\nafter\n',
                 '\\sum_i y', 'jimbeamerMathDisplay', id='dollar-maths'),
])
def test_only_a_line_that_opens_a_fence_ends_them(tmp_path, deck, needle,
                                                  group):
    """The other side of the guard above.  '===' and '$$' and '\\[' all
hold text, so the pattern is the whole of a fence's opening line and not
merely a run of backticks somewhere on one -- loosen it and a region ends
on its own contents.  Three backticks mid-line is the worst case rather
than a deck shape: it is what tells a sloppy guard from this one."""
    probed = run_vim(tmp_path, deck)
    assert group in groups_on(probed, needle)


@vim_needed
def test_a_commented_out_listing_stays_a_comment(tmp_path):
    """The exception to the rule above, and the reason '<!--' is two
regions rather than one.  Beginning a line it is an HTML block, and the
converter removes the block whole -- a listing inside one is comment and
not a listing.  Ending it at a fence, the way the inline '<!--' now ends,
would colour a commented-out slide as live code."""
    probed = run_vim(tmp_path, '# S\n\n<!--\n```C\nint hidden;\n```\n-->\n\n'
                               'after the comment\n')
    assert 'jimbeamerHtmlComment' in groups_on(probed, 'int hidden;')
    assert 'jimbeamerCodeFence' not in groups_on(probed, 'int hidden;')
    assert not groups_on(probed, 'after the comment')


@vim_needed
def test_a_code_span_is_closed_by_a_run_of_its_own_length(tmp_path):
    """CommonMark's rule, and the one markdown.vim's own region broke: it
closed a run of any length with the first backtick of the next run, so
'`a ``` b`' ended in the middle and the rest of the paragraph was coloured
back to front.  Ending a span at a fence, which is what the case above
needed, does not cover this one -- there is no fence line here to end
anything."""
    probed = run_vim(tmp_path,
                     '# S\n\na `span with ``` three in it` and so on\n'
                     'plain prose\n')
    assert 'jimbeamerInlineCode' in groups_on(probed, 'a `span with')
    assert 'jimbeamerInlineCode' not in groups_on(probed, 'plain prose')


@vim_needed
def test_a_backtick_inside_a_links_text_swallows_nothing(tmp_path):
    """markdown.vim's code span is in its @markdownInline cluster, so
markdownLinkText can still reach it however ours is defined, and from in
there it ran to the end of the file as it always did.  Clearing it is what
stops that, and the cost is recorded beside the rule: a code span inside a
link's text is no longer told apart from the link text."""
    probed = run_vim(tmp_path, '# S\n\n[link `a](http://x)\n'
                               '```C\nint body;\n```\n')
    assert 'jimbeamerCodeFence' in groups_on(probed, 'int body;')


@vim_needed
@pytest.mark.parametrize('closer, closes', [
    pytest.param('```', True, id='same-length'),
    pytest.param('`````', True, id='longer'),
    pytest.param('``', False, id='shorter'),
    pytest.param('~~~', False, id='other-character'),
    pytest.param('``` done', False, id='info-string'),
])
def test_the_closing_fence_matches_the_converter(tmp_path, closer, closes):
    """Issue #23: the syntax file wanted a closer of exactly the opener's
length, where the converter takes one at least as long. A deck closing
'```' with '`````' had the rest of the file coloured as code."""
    probed = run_vim(tmp_path, '# S\n\n```C\nint x;\n%s\n\nafter the fence\n'
                               % closer)
    coloured = 'jimbeamerCodeFence' in groups_on(probed, 'after the fence')
    assert coloured == (not closes)


@vim_needed
@pytest.mark.parametrize('trailer, closes', [
    pytest.param(' ', True, id='space'),
    pytest.param('\t', True, id='tab'),
    pytest.param('\u00a0', False, id='nbsp'),
    pytest.param('\u2000', False, id='en-quad'),
])
def test_the_closing_fence_takes_the_spaces_the_converter_takes(tmp_path,
                                                                render,
                                                                trailer,
                                                                closes):
    """Issue #26. CommonMark lets spaces and tabs follow a closer and
nothing else, and vim's '\\s' is those two. CLOSE_RE said '[^\\n\\S]',
where '\\S' on a str pattern is Unicode aware, so every space Unicode
knows of closed the fence for the converter and none of them for the
syntax file: a listing with a no-break space after its backticks was
coloured as code to the end of the deck and converted as prose.

Both are asked here, because a test of either on its own passes happily
while the two disagree -- which is how this lasted."""
    deck = '# S\n\n```C\nint x;\n```%s\n\nafter the fence\n' % trailer
    probed = run_vim(tmp_path, deck)
    coloured = 'jimbeamerCodeFence' in groups_on(probed, 'after the fence')
    outside = 'after the fence' in render(deck).split('\\end{lstlisting}')[-1]
    assert coloured == (not closes)
    assert outside == closes


@vim_needed
@pytest.mark.parametrize('indent, closes', [
    pytest.param('    ', True, id='aligned'),
    pytest.param('', True, id='at-the-margin'),
    pytest.param('   ', True, id='three-from-the-margin'),
    pytest.param('       ', True, id='three-past-the-opener'),
    pytest.param('        ', False, id='four-past-the-opener'),
    pytest.param('\t', False, id='a-tab-is-four-columns'),
])
def test_the_closing_fence_may_not_outdent_the_opener(tmp_path, indent,
                                                      closes):
    """The other half of issue #23. The region took a closer at any indent,
so a listing quoting a bare fence further in than a closer may be --
a deck explaining this format -- ended there, and everything after it was
coloured back to front.

A closer three columns from the margin or fewer closes whatever the opener
was, since no indent is negative and three is therefore always within
"opener plus three".  That is the second end pattern, and
'three-from-the-margin' is it.

The tab case is why the slack is three spaces rather than three \\s: a tab
is four columns and so is already too far, but it is one character."""
    probed = run_vim(tmp_path, '# S\n\n    ```C\n    int x;\n%s```\n\n'
                               'after the fence\n' % indent)
    coloured = 'jimbeamerCodeFence' in groups_on(probed, 'after the fence')
    assert coloured == (not closes)


@vim_needed
@pytest.mark.parametrize('mark', ['```', '~~~'], ids=['backtick', 'tilde'])
@pytest.mark.parametrize('pad', ['        ', '\t\t'], ids=['spaces', 'tabs'])
def test_a_listing_quoting_a_bare_fence_keeps_its_colour(tmp_path, mark, pad):
    """Issue #23 as it is actually met: one bare fence quoted inside a
listing. Both lines below belong to the listing and the one after it does
not, and the file used to say the opposite of all three.

Over both fence characters, because the regions are two separate code
paths now and only the backtick one was ever pinned here."""
    probed = run_vim(tmp_path, '# S\n\n%smarkdown\nclose one with\n\n%s%s\n\n'
                               'still inside the listing\n%s\n\n'
                               'after the fence\n' % (mark, pad, mark, mark))
    assert 'jimbeamerCodeFence' in groups_on(probed, 'still inside the listing')
    assert 'jimbeamerCodeFence' not in groups_on(probed, 'after the fence')


@vim_needed
def test_a_backtick_in_the_info_string_opens_nothing(tmp_path):
    """CommonMark's rule and marko's: a backtick fence's info string may
not hold a backtick, so this is a paragraph with a code span in it. The
converter has always known; the syntax file opened a region and coloured
the rest of the deck."""
    probed = run_vim(tmp_path, '# S\n\n```a``` b\n\nafter the fence\n')
    assert 'jimbeamerCodeFence' not in groups_on(probed, 'after the fence')


@vim_needed
def test_a_backtick_may_sit_in_a_tilde_fences_info_string(tmp_path):
    """The no-backtick rule is CommonMark's and binds a backtick fence
only, so this opens a listing where '```a``` b' does not. It is the
reason the two regions have start patterns of their own rather than one
shared one; merged, this line stops being a fence."""
    probed = run_vim(tmp_path, '# S\n\n~~~a``` b\nint x;\n~~~\n\n'
                               'after the fence\n')
    assert 'jimbeamerCodeFence' in groups_on(probed, 'int x;')
    assert 'jimbeamerCodeFence' not in groups_on(probed, 'after the fence')


@vim_needed
@pytest.mark.parametrize('closer', ['```~~~', '~~~```'],
                         ids=['backtick-first', 'tilde-first'])
def test_a_fence_is_not_closed_by_a_run_of_both(tmp_path, closer):
    """A closer is one character repeated and nothing else, so neither of
these closes anything -- the converter's CLOSE_RE matches one run and
then insists on the end of the line.

Only 'backtick-first' pays for the split: merge the regions, let '[`~]*'
carry the extra length, and that one starts closing the fence.
'tilde-first' never matches \\z2 at the start of the line either way, so it
is a plain regression guard rather than evidence for the split."""
    probed = run_vim(tmp_path, '# S\n\n```C\nint x;\n%s\n\n'
                               'after the fence\n' % closer)
    assert 'jimbeamerCodeFence' in groups_on(probed, 'after the fence')


@vim_needed
def test_a_tilde_fence_is_closed_by_tildes_only(tmp_path):
    """The regions are split on the fence character so that a longer
closer can be spelled at all; this is the half of that which must not
regress."""
    probed = run_vim(tmp_path, '# S\n\n~~~C\nint x;\n```\n\nafter the fence\n')
    assert 'jimbeamerCodeFence' in groups_on(probed, 'after the fence')


@vim_needed
def test_a_verbatim_environment_is_not_ended_by_a_hash(tmp_path):
    """The exception the converter makes: inside VERBATIM_ENVIRONMENTS a
'# ' line is a shell or Python comment, not a heading, so only the
matching \\end closes it."""
    probed = run_vim(tmp_path, '# S\n\n\\begin{verbatim}\n# not a heading\n'
                               '\\end{verbatim}\n')
    assert 'jimbeamerHeading' not in groups_on(probed, '# not a heading')


@vim_needed
@pytest.mark.parametrize('needle', [
    pytest.param('<!--lang: en-->', id='html'),
    pytest.param('% a note', id='percent'),
])
def test_both_metadata_comments_are_comments(tmp_path, needle):
    """YAML_COMMENT_RE takes both out before the block is read."""
    probed = run_vim(tmp_path, '---\ntitle: T\n<!--lang: en-->\n% a note\n'
                               '---\n\n# S\n\nx\n')
    assert 'jimbeamerMetaComment' in groups_on(probed, needle)


@vim_needed
def test_a_deck_whose_directive_is_indented_is_still_a_deck(tmp_path):
    """ftdetect decides by content, and it capped a directive at three
spaces as the syntax file did -- so a deck written in the style this
format now allows, with everything lined up under a bullet, was not
recognised as one at all."""
    source = tmp_path / 'deep.md'
    source.write_text('# S\n\n* outer\n  * inner\n\n    @minipage 6cm\n'
                      '    \\input{figs/x}\n    @end minipage\n',
                      encoding='utf-8')
    out = tmp_path / 'ft.txt'
    subprocess.run(
        [VIM, '-N', '-u', 'NONE', '-i', 'NONE',
         '--cmd', 'set runtimepath^=%s' % VIM_DIR, '--cmd', 'filetype on',
         '-c', "call writefile([&filetype], '%s')" % out,
         '-c', 'quit!', str(source)],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, timeout=60, check=False)
    assert out.read_text(encoding='utf-8').strip() == 'jimbeamer'


@vim_needed
def test_the_ftplugin_teaches_gq_what_a_marker_is(buffer_options):
    """Indentation carries meaning now, and re-wrapping without these
flattens it.  'n' keeps a numbered list's hanging indent, and the pattern
says what a marker looks like here -- '(a)', 'a)', '(iv)' and '2.' as
well as the bullets vim already knows."""
    assert 'n' in buffer_options['formatoptions']
    assert '[ivxlcdm]' in buffer_options['formatlistpat']


def test_the_syntax_file_knows_every_slide_metadata_key(jimbeamer):
    """Nearly every rule in the syntax file matches a shape -- any 'key:',
any '.class', any '@directive' -- and so cannot fall behind the
converter.  jimbeamerSlideKey is the exception: it lists the keys a slide
understands, to tell them from one the converter will warn about.  A key
added to SLIDE_METADATA_KEYS and not here would simply stop being
coloured, and nothing would notice.

Reads the file rather than vim, so it runs where vim is not installed.
"""
    with io.open(os.path.join(VIM_DIR, 'syntax', 'jimbeamer.vim'),
                 encoding='utf-8') as handle:
        source = handle.read()
    match = re.search(r'jimbeamerSlideKey\s*\n\s*\\ /\^\\s\*\\%\((.+?)\\\)',
                      source)
    assert match, 'jimbeamerSlideKey is not where this test expects it'
    assert set(match.group(1).split('\\|')) == set(jimbeamer.SLIDE_METADATA_KEYS)


@vim_needed
def test_a_percent_line_is_a_comment_in_the_metadata_too(tmp_path):
    """The converter takes a '%' line out of a metadata block before the
YAML is read, in the document's block and in a slide's own.  The syntax
file knew only '#', which YAML itself understands."""
    probed = run_vim(tmp_path, '---\ntitle: T\n% theme: metropolis\n---\n\n'
                               '# S\n\n===\ntitle: A\n% itemsep: 1em\n'
                               'label: here\n---\n\n* x\n')
    assert 'jimbeamerMetaComment' in groups_on(probed, '% theme: metropolis')
    assert 'jimbeamerMetaComment' in groups_on(probed, '% itemsep: 1em')


def test_the_example_deck_is_recognized_as_ours(example):
    """And that it is this syntax doing the work, not markdown's alone."""
    seen = {group for _, groups in example for group in groups}
    assert {'jimbeamerDirective', 'jimbeamerMath', 'jimbeamerSlideKey'} <= seen


###########################################
# filetype detection
###########################################

# A deck is an ordinary '.md', so detection reads the file.  All the cases
# go through one vim, since starting it is the slow part.
DETECT_CASES = {
    'directive.md': '# D\n\n@theorem[X]\nbody\n@end\n',
    'slidemeta.md': '# D\n\n===\ntitle: T\n---\n\nx\n',
    'pause.md': '# D\n\n* a\n\\pausex\n* b\n',
    'plain.md': '# Ordinary\n\n* a list\n\nand a@b.com address\n',
    'about.md': ('# About the format\n\nA slide may say what it is:\n\n'
                 '```markdown\n===\ntitle: T\n---\n\n@columns\n@end\n'
                 '```\n\nand that is all.\n'),
    'explicit.jimd': '# No markers at all\n\n* just bullets\n',
}


@pytest.fixture(scope='module')
def buffer_options(tmp_path_factory):
    """The options vim's ftplugin machinery leaves on a deck."""
    if VIM is None:
        pytest.skip('vim is not installed')

    work = tmp_path_factory.mktemp('ftplugin')
    (work / 'deck.md').write_text(SAMPLE, encoding='utf-8')
    out = work / 'opts.json'
    subprocess.run(
        [VIM, '-N', '-u', 'NONE', '-i', 'NONE',
         '--cmd', 'set runtimepath^=%s' % VIM_DIR,
         '--cmd', 'filetype plugin on',
         '-c', "call writefile([json_encode({'filetype': &filetype, "
               "'commentstring': &commentstring, 'comments': &comments, "
               "'formatoptions': &formatoptions, "
               "'formatlistpat': &formatlistpat})], '%s')" % out,
         '-c', 'quit!', str(work / 'deck.md')],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, timeout=60, check=False)

    assert out.exists(), 'vim wrote no result; the ftplugin may not load'
    return json.loads(out.read_text(encoding='utf-8'))


@vim_needed
def test_the_ftplugin_offers_the_comment_this_format_has(buffer_options):
    """A deck is an ordinary '.md' file, so vim loads its markdown
ftplugin first and that sets commentstring to an HTML comment.  Without
an ftplugin of ours the buffer keeps whatever that left behind, and every
comment plugin -- 'gcc' and the rest -- wraps a line in it.

'%' is the comment this format has: the converter removes such a line
before anything parses the document.  '<!-- ... -->' is dropped too, but
it is an HTML block, and one between two list items splits the list in
two, which is a defect in TODO.md.  A '%' line does not.  It is also
one-sided, so there is no closing half for a plugin to leave off."""
    assert buffer_options['filetype'] == 'jimbeamer'
    assert buffer_options['commentstring'] == '% %s'
    assert buffer_options['comments'] == ':%'


@pytest.fixture(scope='module')
def detected(tmp_path_factory):
    """The filetype vim settles on, for each of the cases above."""
    if VIM is None:
        pytest.skip('vim is not installed')

    work = tmp_path_factory.mktemp('detect')
    cases = dict(DETECT_CASES)
    with open(os.path.join(os.path.dirname(HERE), 'README.md'),
              encoding='utf-8') as handle:
        cases['README.md'] = handle.read()

    for name, text in cases.items():
        (work / name).write_text(text, encoding='utf-8')

    out = work / 'ft.json'
    # 'filetype on' has to happen before the files are read, or no BufRead
    # autocommand ever runs and every filetype comes back empty
    subprocess.run(
        [VIM, '-N', '-u', 'NONE', '-i', 'NONE',
         '--cmd', 'set runtimepath^=%s' % VIM_DIR,
         '--cmd', 'filetype on',
         '-c', 'let g:ft = {}',
         '-c', "argdo let g:ft[expand('%:t')] = &filetype",
         '-c', "call writefile([json_encode(g:ft)], '%s')" % out,
         '-c', 'qall!'] + [str(work / name) for name in cases],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, timeout=60, check=False)

    assert out.exists(), 'vim wrote no result'
    return json.loads(out.read_text(encoding='utf-8'))


@vim_needed
@pytest.mark.parametrize('name', [
    pytest.param('directive.md', id='directive'),
    pytest.param('slidemeta.md', id='slide-metadata'),
    pytest.param('pause.md', id='pause'),
    pytest.param('explicit.jimd', id='by-extension'),
])
def test_a_deck_is_detected(detected, name):
    assert detected[name] == 'jimbeamer'


@vim_needed
def test_plain_markdown_is_left_alone(detected):
    assert detected['plain.md'] == 'markdown'


@vim_needed
def test_a_document_about_the_format_is_not_a_deck(detected):
    """Fenced code is skipped while looking, or a document explaining the
format detects as one written in it."""
    assert detected['about.md'] == 'markdown'


@vim_needed
def test_the_readme_is_not_a_deck(detected):
    """The real one, which is where that was first noticed."""
    assert detected['README.md'] == 'markdown'
