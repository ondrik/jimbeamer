---
layout: default
---

<style>
/* Tabs with no JavaScript: a radio per tab, and the panel that follows the
   checked one is the one shown.  The order matters -- every input and
   label first, then the panels -- because the rules below reach the panel
   from the input with a sibling selector, which only looks forwards. */
.tabs input { position: absolute; opacity: 0; pointer-events: none; }
.tabs { border-bottom: 1px solid #e0e0e0; margin-bottom: 1.5rem; }
.tabs label {
  display: inline-block;
  padding: 0.5rem 1rem;
  margin-bottom: -1px;
  cursor: pointer;
  color: #606c71;
  border-bottom: 3px solid transparent;
}
.tabs label:hover { color: #159957; }
.tabs input:focus-visible + label { outline: 2px solid #159957; }
.tabs .panel { display: none; padding-top: 1rem; }
.tabs input:nth-of-type(1):checked ~ label:nth-of-type(1),
.tabs input:nth-of-type(2):checked ~ label:nth-of-type(2),
.tabs input:nth-of-type(3):checked ~ label:nth-of-type(3),
.tabs input:nth-of-type(4):checked ~ label:nth-of-type(4) {
  color: #159957;
  font-weight: 600;
  border-bottom-color: #159957;
}
.tabs input:nth-of-type(1):checked ~ .panel:nth-of-type(1),
.tabs input:nth-of-type(2):checked ~ .panel:nth-of-type(2),
.tabs input:nth-of-type(3):checked ~ .panel:nth-of-type(3),
.tabs input:nth-of-type(4):checked ~ .panel:nth-of-type(4) { display: block; }
.tabs .panel > :first-child { margin-top: 0; }
</style>

<div class="tabs">

<input type="radio" name="tab" id="tab-what" checked>
<input type="radio" name="tab" id="tab-install">
<input type="radio" name="tab" id="tab-example">
<input type="radio" name="tab" id="tab-more">
<label for="tab-what">What it is</label>
<label for="tab-install">Install</label>
<label for="tab-example">An example</label>
<label for="tab-more">More</label>

<div class="panel" markdown="1">

A lightweight alternative to `pandoc -t beamer`, built on
[marko](https://github.com/frostming/marko).

The guiding principle is **LaTeX passthrough**: whatever the Markdown parser
does not recognise is assumed to be LaTeX and emitted untouched. That is why
a slide can always fall back to raw LaTeX, why `\begin{align}` and `@theorem`
both work without the tool knowing either name, and why you can write
`$pc_1 \land pc_2$` in the middle of a bullet and get exactly that back.

</div>

<div class="panel" markdown="1">

```console
$ pipx install jimbeamer
```

[pipx](https://pipx.pypa.io/) puts the command on your `PATH` in an
environment of its own. Then:

```console
$ jimbeamer deck.jimd -o deck.tex     # convert
$ jimbeamer --pdf deck.jimd           # convert, and build the PDF
```

`--pdf` wants a LaTeX installation; converting does not.

</div>

<div class="panel" markdown="1">

```markdown
---
title: 'Symbolic Execution'
author: 'Jan Novák'
theme: Madrid
---

# What it does

* executes a program on **symbolic** inputs
* builds a path condition $pc_1 \land pc_2$

@theorem[Pumping lemma]
For every *regular* language $L$ there is an $n$.
@end
```

becomes a title page and a frame holding an `itemize` and a `theorem`.

</div>

<div class="panel" markdown="1">

Every construct, written out for the deck author, is in the
[README](https://github.com/ondrik/jimbeamer#readme): metadata, slides and
their own settings, lists that count how they are written, maths in four
spellings, listings, columns, environments, figures, and a block for LaTeX
that belongs in the preamble.

* [Source](https://github.com/ondrik/jimbeamer) — MIT licensed
* [On PyPI](https://pypi.org/project/jimbeamer/)
* [Vim syntax file](https://github.com/ondrik/jimbeamer/tree/master/vim),
  for the input format

</div>

</div>
