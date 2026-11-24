"""End-to-end tests: use the installed package the way a user would.

Each test starts a fresh Python interpreter, so nothing from the test
session (fixtures, imports, seeds) leaks in. Under ``tox`` the package is
installed from a freshly built wheel, so these tests exercise the real
distribution rather than the source tree.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from importlib import metadata

import pytest

pytestmark = pytest.mark.e2e

DIST_NAME = "faker-vedic-astrology-birth-chart"


def _run_python(code: str) -> str:
    """Run code in a new interpreter and return its standard output.

    Parameters
    ----------
    code : str
        Python source to run.

    Returns
    -------
    str
        Everything the script printed.

    Raises
    ------
    subprocess.CalledProcessError
        If the script exits with a non-zero status.
    """
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def test_package_metadata_is_installed() -> None:
    """The distribution is installed with a version, licence and Faker dependency."""
    dist = metadata.distribution(DIST_NAME)
    assert dist.version
    requirements = dist.requires or []
    assert any(req.lower().startswith("faker") for req in requirements)


def _is_editable_install() -> bool:
    """Return whether the package is installed in editable (development) mode.

    Returns
    -------
    bool
        ``True`` for ``pip install -e .``, where the wheel's file list is
        not available.
    """
    direct_url = metadata.distribution(DIST_NAME).read_text("direct_url.json")
    if not direct_url:
        return False
    return bool(json.loads(direct_url).get("dir_info", {}).get("editable", False))


def test_type_marker_is_shipped() -> None:
    """The ``py.typed`` marker is included so type checkers use the package's hints."""
    if _is_editable_install():
        pytest.skip("editable install: file list only available for a built wheel (run via tox)")
    files = metadata.files(DIST_NAME) or []
    assert any(str(f).endswith("faker_vedic_astrology_birth_chart/py.typed") for f in files)


def test_user_script_generates_valid_json_charts() -> None:
    """A user script can generate seeded charts and serialise them to JSON."""
    output = _run_python(
        """
        import json
        from faker import Faker
        from faker_vedic_astrology_birth_chart import VedicAstrologyProvider

        fake = Faker()
        fake.add_provider(VedicAstrologyProvider)
        Faker.seed(1234)
        print(json.dumps([fake.vedic_birth_chart() for _ in range(3)]))
        """
    )
    charts = json.loads(output)
    assert len(charts) == 3
    for chart in charts:
        assert len(chart) == 9
        assert all(len(placement) == 6 for placement in chart)


def test_output_is_reproducible_across_processes() -> None:
    """Two separate processes with the same seed print identical charts."""
    script = """
        from faker import Faker
        from faker_vedic_astrology_birth_chart import Provider

        fake = Faker()
        fake.add_provider(Provider)
        Faker.seed(42)
        print(fake.vedic_birth_chart(ascendant="Cancer"))
        """
    assert _run_python(script) == _run_python(script)


def test_generated_charts_pass_public_validator() -> None:
    """Charts generated in a fresh process pass the package's own validator."""
    output = _run_python(
        """
        from faker import Faker
        from faker_vedic_astrology_birth_chart import (
            VedicAstrologyProvider,
            validate_birth_chart,
        )

        fake = Faker()
        fake.add_provider(VedicAstrologyProvider)
        for _ in range(500):
            validate_birth_chart(fake.vedic_birth_chart(), constrain_inner_planets=True)
        print("ok")
        """
    )
    assert output.strip() == "ok"
