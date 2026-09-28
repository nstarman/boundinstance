"""Execute the examples in docstrings and documentation."""

from doctest import ELLIPSIS, NORMALIZE_WHITESPACE

from sybil import Sybil
from sybil.parsers import myst, rest

optionflags = ELLIPSIS | NORMALIZE_WHITESPACE

markdown = Sybil(
    parsers=[
        myst.DocTestDirectiveParser(optionflags=optionflags),
        myst.PythonCodeBlockParser(doctest_optionflags=optionflags),
        myst.SkipParser(),
    ],
    patterns=["*.md"],
)
python = Sybil(
    parsers=[
        rest.DocTestParser(optionflags=optionflags),
        rest.PythonCodeBlockParser(),
        rest.SkipParser(),
    ],
    patterns=["*.py"],
)

pytest_collect_file = (markdown + python).pytest()
