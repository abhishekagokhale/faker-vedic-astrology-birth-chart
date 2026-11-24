"""End-to-end test that every Python example in the README runs.

A broken README snippet fails CI, so the documentation cannot drift away
from the real behaviour of the package.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e

README = Path(__file__).resolve().parents[2] / "README.md"
_CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _python_blocks() -> list[str]:
    """Return every fenced ``python`` code block in the README.

    Returns
    -------
    list of str
        Source code of each block, in order.
    """
    return _CODE_BLOCK.findall(README.read_text(encoding="utf-8"))


def test_readme_has_python_examples() -> None:
    """The README contains at least one Python example to test."""
    assert _python_blocks()


@pytest.mark.parametrize("index", range(len(_python_blocks())))
def test_readme_example_runs(index: int) -> None:
    """Each README example runs without raising, in its own namespace."""
    exec(compile(_python_blocks()[index], f"README.md[block {index}]", "exec"), {})
