# Contributing

Thanks for helping improve `faker-vedic-astrology-birth-chart`.

## Project layout

```
src/faker_vedic_astrology_birth_chart/
    constants.py   # static reference data: planets, signs, nakshatras, retrograde rates
    zodiac.py      # pure functions: longitude <-> sign/degree/nakshatra/house
    chart.py       # chart generation (takes a random.Random) and validation
    provider.py    # the Faker BaseProvider subclass - a thin layer over chart.py
tests/
    unit/          # one file per module, no Faker needed except via fixtures
    integration/   # provider registered with a real Faker; statistical checks
    e2e/           # fresh interpreter against the installed wheel; README examples
```

Keep randomness out of `zodiac.py`. New generation logic goes in `chart.py`
as a function that takes a `random.Random`; the provider just passes in
`self.generator.random` so `Faker.seed()` keeps working.

## Setting up

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip          # pip >= 25.1 is needed for --group
pip install -e . --group dev
pre-commit install
```

## Running checks

| Command | What it does |
|---|---|
| `pytest` | Run all tests (including doctests) in your current environment |
| `pytest -m "not e2e"` | Skip the slower end-to-end tests |
| `tox` | Every Python version you have installed, plus lint, type and package checks, each in its own isolated virtual environment |
| `tox -e py313` | Tests on one Python version |
| `tox -e lint` | Ruff lint and format check |
| `tox -e type` | mypy in strict mode |
| `tox -e pkg` | Build the sdist and wheel and run `twine check` |
| `tox -e format` | Auto-fix lint issues and reformat |
| `tox p` | Run all environments in parallel |

Coverage must stay at or above 95%.

## Code style

- Ruff handles linting and formatting (line length 100).
- mypy runs in strict mode on both `src` and `tests`.
- Every module, class, function and method has a NumPy-style docstring
  (<https://numpydoc.readthedocs.io/en/latest/format.html>); Ruff enforces this.
- Every test has a one-line docstring saying what it checks and what the
  expected behaviour is.

## Releasing

### One-time PyPI setup (Trusted Publishing)

1. Sign in to <https://pypi.org> and open **Your account → Publishing**.
2. Under **Add a new pending publisher**, enter:
   - PyPI project name: `faker-vedic-astrology-birth-chart`
   - Owner: `abhishekagokhale`
   - Repository: `faker-vedic-astrology-birth-chart`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. Repeat on <https://test.pypi.org> with environment name `testpypi` if you
   want to test releases first.
4. In GitHub, go to **Settings → Environments** and create environments named
   `pypi` and `testpypi` (optionally requiring your approval).

No API tokens are needed.

### Each release

1. Update `version` in `pyproject.toml` and add a section to `CHANGELOG.md`.
2. Merge to `main` and wait for CI to pass.
3. Optional dry run: **Actions → Publish to PyPI → Run workflow → testpypi**.
4. Create a GitHub Release with tag `vX.Y.Z` matching the version. Publishing
   the release triggers the upload to PyPI.
