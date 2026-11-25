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

This project uses [Poetry](https://python-poetry.org/) (2.2 or later) to manage
the virtual environment and dependencies. The package itself is still built by
hatchling, so the published wheel does not depend on Poetry.

1. Install Python 3.11 or later (3.13 recommended), e.g. from
   [python.org](https://www.python.org/downloads/). Poetry itself needs
   Python 3.10 or later to run.

2. Install Poetry (once per machine). Either use pipx:

   ```bash
   pipx install poetry
   ```

   or the official installer:

   ```bash
   # macOS / Linux
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   ```powershell
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
   ```

   Check it works with `poetry --version`. If the command is not found, add
   the folder the installer printed to your `PATH` and open a new terminal.

3. From the project folder, create the environment:

   ```bash
   poetry env use 3.13   # optional: choose the Python version
   poetry sync
   ```

   This creates a virtual environment and installs the package in editable
   mode plus every development tool, at the exact versions in `poetry.lock`.
   By default Poetry keeps the environment in its own cache folder, outside
   the project; `poetry env info --path` shows where.

4. Optionally, install the git hooks:

   ```bash
   poetry run pre-commit install
   ```

### Using an IDE

In PyCharm: **Settings → Python → Interpreter → Add Interpreter → Add Local
Interpreter**, choose **Poetry**, then **Select existing** and pick this
project's environment. If PyCharm does not find Poetry, browse to the
`poetry` executable (`where poetry` on Windows, `which poetry` elsewhere).
Then set **Tools → Python Integrated Tools → Default test runner** to `pytest`.

Other IDEs: point them at the Python inside `poetry env info --path`.

### Working in a synced folder (Dropbox, OneDrive)

Poetry's default keeps the environment outside the project folder, so a sync
client never sees it. If you change that with
`poetry config virtualenvs.in-project true`, tell the sync client to ignore
the resulting `.venv`, for example with Dropbox:

```powershell
# Windows (PowerShell)
Set-Content -Path .venv -Stream com.dropbox.ignored -Value 1
```

```bash
# macOS
xattr -w com.dropbox.ignored 1 .venv
```

## Managing dependencies

`pyproject.toml` declares the **ranges** each dependency may use, using the
standard `[project]` and PEP 735 `[dependency-groups]` tables.
`poetry.lock` records the **exact versions and hashes** resolved from those
ranges, for every supported platform and Python version. Always commit both.

| Task | Command |
|---|---|
| Install exactly what is locked | `poetry sync` |
| Add a development tool | `poetry add --group test hypothesis` |
| Remove a development tool | `poetry remove --group test hypothesis` |
| Update locked versions within the ranges | `poetry update --lock` |
| Update one package in the lock | `poetry update --lock faker` |
| Re-resolve the lock from scratch | `poetry lock --regenerate` |
| Check the lock matches `pyproject.toml` | `poetry check --lock` |

After editing `pyproject.toml` by hand, run `poetry lock` to bring
`poetry.lock` back in step.

The package itself is a **library**, so its runtime dependency must stay a
loose range (`Faker>=30.0`). Never pin it to one exact version in
`pyproject.toml`: that would clash with the Faker version in users' own
projects. Raise the lower bound only when the code genuinely needs a newer
Faker, and update the `deps` line of the `lowest` tox environment to match.

Dependabot opens monthly pull requests to refresh `poetry.lock`. It only
changes a range in `pyproject.toml` when a new release falls outside it.

## Running checks

| Command | What it does |
|---|---|
| `poetry run pytest` | Run all tests (including doctests) in the Poetry environment |
| `poetry run pytest -m "not e2e"` | Skip the slower end-to-end tests |
| `poetry run tox` | Every environment below, each in its own isolated virtual environment |
| `poetry run tox -e py313` | Tests on one Python version, with locked dependencies |
| `poetry run tox -e lowest` | Tests the built wheel with the oldest Faker allowed (30.0) |
| `poetry run tox -e latest` | Tests the built wheel with the newest versions on PyPI, ignoring `poetry.lock` |
| `poetry run tox -e lint` | Ruff lint and format check |
| `poetry run tox -e type` | mypy in strict mode |
| `poetry run tox -e pkg` | Build the sdist and wheel and run `twine check` |
| `poetry run tox -e format` | Auto-fix lint issues and reformat |
| `poetry run tox p` | Run all environments in parallel |

Each tox environment is created by tox and then filled by `poetry sync` from
`poetry.lock`. tox needs each Python version you test to be installed
already; versions you do not have are skipped. Coverage must stay at or
above 95%.

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
2. Run `poetry check --lock`, merge to `main` and wait for CI to pass.
3. Optional dry run: **Actions → Publish to PyPI → Run workflow → testpypi**.
4. Create a GitHub Release with tag `vX.Y.Z` matching the version. Publishing
   the release runs the full CI again and, if it passes, uploads to PyPI.
