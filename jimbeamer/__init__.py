"""Convert Markdown into LaTeX Beamer slides.

A lightweight alternative to `pandoc -t beamer', built on marko.  The guiding
principle is LaTeX passthrough: whatever the Markdown parser does not
recognize is handed over to LaTeX untouched, so a slide can always fall back
to raw LaTeX.

The converter itself is jimbeamer.jimbeamer; this exposes only what a caller
needs, so that importing the package does not drag in marko until it is
wanted.
"""

from jimbeamer._version import VERSION

__version__ = VERSION
__all__ = ['VERSION', '__version__', 'main']


def main():
    """main() -> None: the command, as installed by pip."""
    from jimbeamer.jimbeamer import main as run
    run()
