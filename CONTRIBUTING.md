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

This project uses [uv](https://docs.astral.sh/uv/) to manage Python versions,
the virtual environment and dependencies.

1. Install uv (once per machine):

   ```bash
   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   ```powershell
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. From the project folder, create the environment:

   ```bash
   uv sync
   ```

   This downloads Python 3.13 if needed (see `.python-version`), creates
   `.venv`, and installs the package in editable mode plus every development
   tool at the exact versions in `uv.lock`.

3. Optionally, install the git hooks:

   ```bash
   uv run pre-commit install
   ```

### Using an IDE

Point your IDE at the interpreter uv created:

- Windows: `.venv\Scripts\python.exe`
- macOS / Linux: `.venv/bin/python`

In PyCharm: **Settings → Project → Python Interpreter → Add Interpreter →
Add Local Interpreter → Select existing**, then set **Tools → Python
Integrated Tools → Default test runner** to `pytest`.

### Working in a synced folder (Dropbox, OneDrive)

`.venv` contains thousands of small files that a sync client will try to
upload. Either tell the sync client to ignore it, for example with Dropbox:

```powershell
# Windows (PowerShell), after `uv sync`
Set-Content -Path .venv -Stream com.dropbox.ignored -Value 1
```

```bash
# macOS
xattr -w com.dropbox.ignored 1 .venv
```

or keep the environment outside the folder by setting
`UV_PROJECT_ENVIRONMENT` to another path before running `uv` commands in
this project.

## Managing dependencies

`pyproject.toml` declares the **ranges** each dependency may use.
`uv.lock` records the **exact versions and hashes** resolved from those
ranges, for every supported platform and Python version. Always commit both.

| Task | Command |
|---|---|
| Install exactly what is locked | `uv sync --locked` |
| Add a development tool | `uv add --group test hypothesis` |
| Remove a development tool | `uv remove --group test hypothesis` |
| Upgrade everything in the lock | `uv lock --upgrade` |
| Upgrade one package in the lock | `uv lock --upgrade-package faker` |
| Check the lock matches `pyproject.toml` | `uv lock --check` |
| Export a standard PEP 751 lock file | `uv export --format pylock.toml -o pylock.toml` |

The package itself is a **library**, so its runtime dependency must stay a
loose range (`Faker>=30.0`). Never pin it to one exact version in
`pyproject.toml`: that would clash with the Faker version in users' own
projects. Raise the lower bound only when the code genuinely needs a newer
Faker, and update the `lowest` test environment's expectations if so.

Dependabot opens monthly pull requests to refresh `uv.lock`. It is told not
to touch Faker's lower bound; refresh Faker in the lock by hand with
`uv lock --upgrade-package faker`.

## Running checks

| Command | What it does |
|---|---|
| `uv run pytest` | Run all tests (including doctests) in `.venv` |
| `uv run pytest -m "not e2e"` | Skip the slower end-to-end tests |
| `uv run tox` | Every environment below, each in its own isolated virtual environment |
| `uv run tox -e py313` | Tests on one Python version, with locked dependencies |
| `uv run tox -e lowest` | Tests with the oldest versions `pyproject.toml` allows (Faker 30.0) |
| `uv run tox -e latest` | Tests with the newest versions on PyPI, ignoring `uv.lock` |
| `uv run tox -e lint` | Ruff lint and format check |
| `uv run tox -e type` | mypy in strict mode |
| `uv run tox -e pkg` | Build the sdist and wheel and run `twine check` |
| `uv run tox -e format` | Auto-fix lint issues and reformat |
| `uv run tox p` | Run all environments in parallel |

tox uses [tox-uv](https://github.com/tox-dev/tox-uv), so test environments are
created by uv from `uv.lock`; any missing Python version is downloaded
automatically. Coverage must stay at or above 95%.

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
2. Run `uv lock --check`, merge to `main` and wait for CI to pass.
3. Optional dry run: **Actions → Publish to PyPI → Run workflow → testpypi**.
4. Create a GitHub Release with tag `vX.Y.Z` matching the version. Publishing
   the release runs the full CI again and, if it passes, uploads to PyPI.
