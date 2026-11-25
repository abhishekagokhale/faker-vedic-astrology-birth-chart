# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Development environment managed with Poetry (2.2+): `poetry.lock` pins
  every development tool to exact, hash-verified versions for all platforms
  and Python versions. The package is still built by hatchling, so the
  published wheel is unchanged.
- tox environments are filled from `poetry.lock` with `poetry sync`, so local
  runs and CI use identical tool versions.
- Pre-commit runs Ruff and mypy through Poetry and checks the lock is current.
- Dependabot refreshes `poetry.lock` without raising minimum versions.
- Publishing to PyPI now requires the full CI workflow to pass first.

### Added

- `lowest` tox environment and CI job: tests the built wheel with the oldest
  Faker `pyproject.toml` allows.
- `latest` tox environment and CI job: tests the built wheel with the newest
  releases, ignoring `poetry.lock`.

## [0.1.0] - 2026-11-22

### Added

- `VedicAstrologyProvider` (also exported as `Provider`) with methods
  `vedic_birth_chart`, `vedic_ascendant`, `vedic_planet_placement`,
  `vedic_retrograde`, `vedic_planet`, `vedic_sign`, `vedic_nakshatra` and
  `vedic_degree`.
- Charts as a tuple of 9 placement dictionaries with keys `planet`, `house`,
  `sign`, `nakshatra`, `degree` and `retrograde`.
- Whole-sign houses counted from a fixed ascendant.
- Nakshatra derived from sign and degree, using the sidereal
  sign-to-nakshatra mapping (`SIGN_NAKSHATRA_MAP`).
- Rahu and Ketu always exactly 180 degrees apart.
- Mercury and Venus kept within their maximum elongation from the Sun
  (optional, on by default).
- Retrograde flags weighted by empirical frequencies.
- `validate_birth_chart` and `InvalidBirthChartError` for checking charts.
- Unit, integration and end-to-end tests; tox environments for Python
  3.11–3.14; Ruff and strict mypy; GitHub Actions CI and PyPI publishing.

[Unreleased]: https://github.com/abhishekagokhale/faker-vedic-astrology-birth-chart/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/abhishekagokhale/faker-vedic-astrology-birth-chart/releases/tag/v0.1.0
