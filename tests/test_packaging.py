"""The things that only matter once the project leaves this directory.

A release is the one thing here that cannot be taken back: PyPI never lets a
filename be used twice, not even after the release is deleted.  So what the
metadata says, what the sdist carries and what the release workflow does are
worth pinning in the suite rather than discovering on the project page.

Nothing here builds anything -- that is CI's job, where the sdist is unpacked
and its own copy of this suite is run.  These are the statements that can be
checked by reading, and each one of them has been wrong at least once.
"""

import io
import os
import re
import subprocess
import sys

import pytest

import conftest

ROOT = conftest.ROOT
WORKFLOWS = os.path.join(ROOT, '.github', 'workflows')
DOCS = os.path.join(ROOT, 'docs')

yaml = pytest.importorskip('yaml')

# The workflows and the landing page have no business in a release, so they
# are not in the sdist -- and CI unpacks the sdist and runs this suite
# inside it.  What they say is checked where they exist, the way the vim
# tests are checked where vim is installed.
in_checkout = pytest.mark.skipif(
    not os.path.isdir(WORKFLOWS) or not os.path.isdir(DOCS),
    reason='not a checkout: workflows and docs are not shipped')


def read(*parts):
    """read(str...) -> str: a file in the checkout, by path components."""
    with io.open(os.path.join(ROOT, *parts), encoding='utf-8') as handle:
        return handle.read()


def front_matter(text):
    """front_matter(str) -> dict

The YAML block at the head of a Jekyll page.  GitHub Pages runs
jekyll-optional-front-matter, so a page without one is still rendered --
what the block is here for is to name the layout.
"""
    match = re.match(r'---\n(.*?)\n---\n', text, re.S)
    assert match, 'no Jekyll front matter'
    return yaml.safe_load(match.group(1)) or {}


def prose_only(markdown):
    """prose_only(str) -> str

Markdown with its code dropped, fenced and inline both.  A link inside
either is an example of the input format, not a link the reader can follow
-- and the fences cannot be paired by a regex, since this README nests a
``` block inside a ```` one.
"""
    kept, fence = [], None
    for line in markdown.splitlines(True):
        match = re.match(r'(`{3,}|~{3,})', line.strip())
        if fence is None:
            if match:
                fence = match.group(1)
            else:
                kept.append(line)
        elif match and match.group(1)[0] == fence[0] \
                and len(match.group(1)) >= len(fence):
            fence = None
    return re.sub(r'`+[^`\n]*`+', '', ''.join(kept))


###########################################
# the metadata, which a release freezes
###########################################

def project():
    """project() -> dict: the [project] table of pyproject.toml."""
    tomllib = pytest.importorskip('tomllib')
    with io.open(os.path.join(ROOT, 'pyproject.toml'), 'rb') as handle:
        return tomllib.load(handle)


def test_the_version_can_be_a_tag(jimbeamer):
    """The release workflow refuses a tag that disagrees with this, so it
has to be something a tag can be spelled as."""
    version = read('jimbeamer', '_version.py')
    match = re.search(r"VERSION = '([^']+)'", version)
    assert match
    assert re.match(r'^\d+\.\d+(\.\d+)?([ab]\d+|rc\d+|\.dev\d+)?$',
                    match.group(1))
    assert jimbeamer.VERSION == match.group(1)


def test_the_marko_floor_is_a_version_that_works():
    """Not the version development started on: 2.2.0 through 2.2.2 collapse
the '\\\\' ending a table row to a single backslash, and the converter says
nothing while pdflatex stops at "Misplaced \\noalign".  A release's
dependencies are frozen with it, so the floor is the one chance to say so."""
    requires = project()['project']['dependencies']
    assert 'marko>=2.2.3' in requires


def test_the_build_backend_floor_can_read_the_license():
    """'license = "MIT"' with license-files is PEP 639, and setuptools
before 77 refuses the file outright.  pip never notices, because build
isolation fetches the newest setuptools; a --no-build-isolation build is
what stops, which is how a distribution packager builds."""
    data = project()
    assert 'setuptools>=77' in data['build-system']['requires']
    assert data['project']['license'] == 'MIT'


###########################################
# the README, which is also the PyPI page
###########################################

def test_the_readme_has_no_relative_links():
    """PyPI serves the description under /project/jimbeamer/, so a link to
TODO.md resolves to pypi.org/project/jimbeamer/TODO.md and 404s.  Four of
these pointed at files that are not even in the sdist."""
    readme = prose_only(read('README.md'))
    relative = [target for target in re.findall(r'\]\(([^)]+)\)', readme)
                if not target.startswith(('http', '#'))]
    assert relative == []


###########################################
# the landing page
###########################################

@in_checkout
def test_the_landing_page_names_a_layout_the_theme_has():
    """jekyll-theme-cayman ships exactly one layout, 'default'.  Misspell
it and the build still succeeds -- a warning in the log, and a bare
fragment served with no banner, no stylesheet and no <html> around it.
Asserting that front matter merely exists would not catch that, and on
GitHub Pages, which runs jekyll-optional-front-matter, it proves nothing."""
    assert front_matter(read('docs', 'index.md'))['layout'] == 'default'


@in_checkout
def test_the_landing_page_says_what_the_package_says():
    """Two descriptions of one tool are two things to keep true."""
    config = yaml.safe_load(read('docs', '_config.yml'))
    assert config['description'] == project()['project']['description']
    assert config['title'] == project()['project']['name']


def test_the_homepage_is_the_landing_page():
    """PyPI shows Homepage and Source side by side, and they are for two
different readers.  Homepage is where GitHub Pages serves docs/."""
    urls = project()['project']['urls']
    assert urls['Homepage'] == 'https://ondrik.github.io/jimbeamer/'
    assert urls['Source'] == 'https://github.com/ondrik/jimbeamer'


@in_checkout
def test_the_landing_page_tabs_line_up():
    """The tabs are CSS and nothing else: a radio per tab, and the panel
that follows the checked one is the one shown.  Which means a tab added
without its panel, or a second 'checked', misaligns every tab after it and
the page still renders -- just showing the wrong thing."""
    page = read('docs', 'index.md')
    inputs = re.findall(r'<input type="radio" name="tab" id="([^"]+)"', page)
    labels = re.findall(r'<label for="([^"]+)">', page)
    assert inputs and inputs == labels
    assert page.count('<div class="panel"') == len(inputs)
    # on an input, not in the selectors or the comment explaining them,
    # which is the same trap the template's own comments set
    assert len(re.findall(r'<input[^>]*\bchecked\b', page)) == 1
    # the selectors are written out one per tab, so they have to keep up
    for index in range(1, len(inputs) + 1):
        assert 'input:nth-of-type(%d):checked ~ .panel:nth-of-type(%d)' % (
            index, index) in page


@in_checkout
def test_the_landing_page_knows_where_it_is_served():
    """The theme links its stylesheet through Jekyll's relative_url, so
without a baseurl the page asks for ondrik.github.io/assets/css/style.css
-- off the end of the project site, and the page arrives unstyled."""
    config = yaml.safe_load(read('docs', '_config.yml'))
    served = '%s%s/' % (config['url'], config['baseurl'])
    assert served == project()['project']['urls']['Homepage']


@in_checkout
def test_the_landing_page_does_not_restate_the_format():
    """One description of the input format, not two that drift apart: the
page shows an example and sends the reader to the README.  The directive
and metadata tables are the README's alone."""
    page = read('docs', 'index.md')
    assert 'github.com/ondrik/jimbeamer#readme' in page
    for table in ('@column', 'short-title', 'itemsep', 'escapechar'):
        assert table not in page


###########################################
# the release workflow
###########################################

def workflow(name):
    """workflow(str) -> dict: a parsed workflow from .github/workflows."""
    with io.open(os.path.join(WORKFLOWS, name), encoding='utf-8') as handle:
        parsed = yaml.safe_load(handle)
    # 'on:' is YAML 1.1's boolean true, which is why it is read this way
    parsed['on'] = parsed.pop(True, parsed.get('on'))
    return parsed


@in_checkout
def test_a_release_is_a_tag():
    assert workflow('release.yml')['on'] == {'push': {'tags': ['v*']}}


def guard_script(tmp_path):
    """guard_script(Path) -> Path

The release's tag check, lifted out of the workflow and made runnable.
'python' is whatever the runner's setup-python left on the PATH, which
here is the interpreter running the tests.
"""
    build = workflow('release.yml')['jobs']['build']
    steps = [step for step in build['steps']
             if 'tag' in step.get('name', '').lower()]
    assert len(steps) == 1, 'one tag guard, or this is testing the wrong one'
    path = tmp_path / 'guard.sh'
    path.write_text(steps[0]['run'].replace('python ', '%s ' % sys.executable),
                    encoding='utf-8')
    return path


@in_checkout
@pytest.mark.parametrize('tag, refused', [
    pytest.param('v%s' % conftest.VERSION_IN_TREE, False, id='agrees'),
    pytest.param('v9.9.9', True, id='disagrees'),
    pytest.param('%s' % conftest.VERSION_IN_TREE, False, id='no-v'),
])
def test_the_release_refuses_a_tag_that_disagrees(tmp_path, tag, refused):
    """Run, not read.  This guard is the whole of what stands between a
mistyped tag and a filename that can never be used again, and a test that
greps it for the word 'exit' would pass against a guard that always
exits 0."""
    done = subprocess.run(
        ['bash', str(guard_script(tmp_path))], cwd=ROOT, text=True,
        env=dict(os.environ, GITHUB_REF_NAME=tag), capture_output=True)
    assert bool(done.returncode) is refused, done.stdout + done.stderr
    if refused:
        assert '9.9.9' in done.stdout


@in_checkout
def test_pypi_comes_last_and_after_something_that_checks():
    """The order is the whole argument for having TestPyPI in the chain at
all: uploading to both in one run proves nothing unless something stands
between them.  Two things do -- this job, which installs what was just
published, and the 'pypi' environment's reviewer, who looks at it."""
    jobs = workflow('release.yml')['jobs']
    assert jobs['testpypi']['needs'] == 'build'
    assert jobs['verify']['needs'] == 'testpypi'
    assert jobs['pypi']['needs'] == 'verify'


@in_checkout
def test_the_rehearsal_is_installed_from_testpypi_and_pinned():
    """Unpinned, pip could satisfy the requirement from a copy an earlier
rehearsal left behind and the step would pass without ever seeing what
this tag published.  And TestPyPI is not a mirror -- its marko stops at
2.0.3 -- so the real index has to be reachable for the dependencies."""
    step = workflow('release.yml')['jobs']['verify']['steps'][-1]['run']
    assert '--index-url https://test.pypi.org/simple/' in step
    assert '--extra-index-url https://pypi.org/simple/' in step
    assert '"jimbeamer==$version"' in step
    assert 'version="${GITHUB_REF_NAME#v}"' in step


@in_checkout
def test_only_the_publishing_jobs_can_mint_a_token():
    """id-token: write is what proves to PyPI who is calling.  The job
that runs pip against an external index is not one of the two that should
be able to."""
    jobs = workflow('release.yml')['jobs']
    for name in ('build', 'verify'):
        assert 'id-token' not in str(jobs[name].get('permissions', ''))
    for name in ('testpypi', 'pypi'):
        assert jobs[name]['permissions'] == {'id-token': 'write'}


@in_checkout
@pytest.mark.parametrize('job', ['testpypi', 'pypi'])
def test_the_upload_jobs_can_prove_who_they_are(job):
    """Trusted Publishing instead of a stored token.  'id-token: write' is
what mints the proof, and it is set per job rather than for the whole
workflow so that the build job never carries it."""
    workflows = workflow('release.yml')
    assert workflows['jobs'][job]['permissions'] == {'id-token': 'write'}
    assert workflows['jobs'][job]['environment'] == job
    assert 'permissions' not in workflows or 'id-token' not in str(
        workflows.get('permissions'))


###########################################
# the sdist
###########################################

def test_the_sdist_ships_a_suite_that_can_run():
    """setuptools' defaults pick up tests/test_*.py by themselves and
nothing else, which is the one wrong answer: the suite arrives without
conftest.py, so it cannot be collected, and without vim/, so test_vim.py
fails rather than skips.  CI unpacks the sdist and runs it; this says what
the file is for."""
    manifest = read('MANIFEST.in')
    named = re.findall(r'(?m)^include (\S+)$', manifest)
    assert sorted(named) == ['pytest.ini', 'tests/conftest.py']
    # a rename would otherwise leave the line matching nothing, silently
    for path in named:
        assert os.path.exists(os.path.join(ROOT, path)), path
    assert 'recursive-include vim *.vim' in manifest
    assert os.path.isdir(os.path.join(ROOT, 'vim'))
