# faker-vedic-astrology-birth-chart

[![CI](https://github.com/abhishekagokhale/faker-vedic-astrology-birth-chart/actions/workflows/ci.yml/badge.svg)](https://github.com/abhishekagokhale/faker-vedic-astrology-birth-chart/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A [Faker](https://github.com/joke2k/faker) community provider that generates
**realistic but synthetic** Vedic (sidereal) astrology birth charts.

> **For testing and development only.** Every chart is random. It does not
> describe any real person or moment in time, and must never be used for real
> consultations or predictions.

## Installation

```bash
pip install faker-vedic-astrology-birth-chart
```

Requires Python 3.11 or later.

## Quick start

```python
from faker import Faker
from faker_vedic_astrology_birth_chart import VedicAstrologyProvider

fake = Faker()
fake.add_provider(VedicAstrologyProvider)

Faker.seed(42)  # optional: makes the output reproducible
chart = fake.vedic_birth_chart()

for placement in chart:
    print(placement)
```

Output (one dictionary per planet; the ascendant here is Aquarius):

```text
{'planet': 'Sun', 'house': 4, 'sign': 'Taurus', 'nakshatra': 'Rohini', 'degree': 15.6, 'retrograde': 'no'}
{'planet': 'Moon', 'house': 3, 'sign': 'Aries', 'nakshatra': 'Ashvini', 'degree': 10.2, 'retrograde': 'no'}
{'planet': 'Mars', 'house': 1, 'sign': 'Aquarius', 'nakshatra': 'Dhanishta', 'degree': 3.7, 'retrograde': 'no'}
{'planet': 'Mercury', 'house': 4, 'sign': 'Taurus', 'nakshatra': 'Rohini', 'degree': 15.7, 'retrograde': 'no'}
{'planet': 'Jupiter', 'house': 6, 'sign': 'Cancer', 'nakshatra': 'Pushya', 'degree': 10.3, 'retrograde': 'no'}
{'planet': 'Venus', 'house': 3, 'sign': 'Aries', 'nakshatra': 'Bharani', 'degree': 21.4, 'retrograde': 'no'}
{'planet': 'Saturn', 'house': 4, 'sign': 'Taurus', 'nakshatra': 'Mrigashirsha', 'degree': 27.1, 'retrograde': 'yes'}
{'planet': 'Rahu', 'house': 1, 'sign': 'Aquarius', 'nakshatra': 'Dhanishta', 'degree': 1.6, 'retrograde': 'yes'}
{'planet': 'Ketu', 'house': 7, 'sign': 'Leo', 'nakshatra': 'Magha', 'degree': 1.6, 'retrograde': 'yes'}
```

## Output format

A birth chart is a **tuple of exactly 9 dictionaries**, one per planet. Each
dictionary has exactly 6 keys, so a chart holds 9 × 6 = 54 values.

| Key          | Type    | Values                                                                 |
|--------------|---------|------------------------------------------------------------------------|
| `planet`     | `str`   | Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu (no repeats) |
| `house`      | `int`   | 1–12, counted from the ascendant (planets may share a house)            |
| `sign`       | `str`   | Aries … Pisces (planets may share a sign)                               |
| `nakshatra`  | `str`   | One of the 27 nakshatras (repeats allowed)                              |
| `degree`     | `float` | 0.0 ≤ degree < 30.0, one decimal place                                  |
| `retrograde` | `str`   | `"yes"` or `"no"`                                                       |

## Rules the generator follows

1. **Ascendant first.** An ascendant (lagna) sign is fixed first and becomes
   house 1. Houses use the whole-sign system, so each house is exactly one sign.
2. **One position per planet.** Each planet gets an absolute sidereal
   longitude. Sign, degree and nakshatra are all derived from it, so they always
   agree. For example, 3.4° Leo is always in Magha.
3. **Rahu and Ketu are always exactly 180° apart.** Only Rahu is drawn; Ketu is
   calculated from it. They always have the same degree, opposite signs, and
   houses six apart.
4. **Mercury and Venus stay near the Sun** (within 28° and 47°), as they do in
   real skies. Turn this off with `constrain_inner_planets=False`.
5. **Retrograde is weighted by how often each planet is retrograde:**

| Planet       | Empirical figure used                 | P(`retrograde="yes"`) |
|--------------|---------------------------------------|-----------------------|
| Sun, Moon    | never retrograde                      | 0                     |
| Rahu, Ketu   | always retrograde                     | 1                     |
| Saturn       | 140 days per 365                      | ≈ 0.384               |
| Jupiter      | 120 days per 365                      | ≈ 0.329               |
| Mercury      | 63–72 (midpoint 67.5) days per 365    | ≈ 0.185               |
| Mars         | 72–80 days every 24–26 months         | ≈ 0.100               |
| Venus        | 40–42 days every 18–19 months         | ≈ 0.073               |

## Provider methods

| Method | Returns |
|---|---|
| `vedic_birth_chart(ascendant=None, constrain_inner_planets=True)` | A full 9-planet chart |
| `vedic_ascendant()` | A random ascendant sign |
| `vedic_planet_placement(planet=None, ascendant=None)` | One stand-alone placement dict |
| `vedic_retrograde(planet)` | `"yes"` or `"no"`, weighted as above |
| `vedic_planet()` | A planet name |
| `vedic_sign()` | A sign name |
| `vedic_nakshatra()` | A nakshatra name |
| `vedic_degree()` | A degree, 0.0–29.9 |

### Knowing the ascendant

The chart itself contains only the nine planets. To know which sign is
house 1, draw the ascendant first and pass it in:

```python
from faker import Faker
from faker_vedic_astrology_birth_chart import VedicAstrologyProvider

fake = Faker()
fake.add_provider(VedicAstrologyProvider)

ascendant = fake.vedic_ascendant()
chart = fake.vedic_birth_chart(ascendant=ascendant)

in_first_house = [p["planet"] for p in chart if p["house"] == 1]
print(f"Ascendant: {ascendant}; planets in house 1: {in_first_house}")
```

### Validating charts

`validate_birth_chart` checks any chart against every rule above and returns
its ascendant. It raises `InvalidBirthChartError` (a `ValueError`) otherwise.
This is handy for testing your own code that produces or transforms charts.

```python
from faker import Faker
from faker_vedic_astrology_birth_chart import (
    InvalidBirthChartError,
    VedicAstrologyProvider,
    validate_birth_chart,
)

fake = Faker()
fake.add_provider(VedicAstrologyProvider)

chart = fake.vedic_birth_chart(ascendant="Cancer")
assert validate_birth_chart(chart) == "Cancer"

broken = tuple({**p, "retrograde": "yes"} if p["planet"] == "Sun" else p for p in chart)
try:
    validate_birth_chart(broken)
except InvalidBirthChartError as error:
    print(error)  # Sun can never be retrograde
```

### Reference data

The sign-to-nakshatra mapping (sidereal degrees within each sign) is
available for your own use:

```python
from faker_vedic_astrology_birth_chart import SIGN_NAKSHATRA_MAP

for segment in SIGN_NAKSHATRA_MAP["Taurus"]:
    print(f"{segment.nakshatra}: {segment.start_degree:.2f}° to {segment.end_degree:.2f}°")
```

### Bulk data

```python
import json

from faker import Faker
from faker_vedic_astrology_birth_chart import VedicAstrologyProvider

fake = Faker()
fake.add_provider(VedicAstrologyProvider)

charts = [fake.vedic_birth_chart() for _ in range(1_000)]
payload = json.dumps(charts)  # charts are plain dicts, so they serialise directly
```

## Development

The development environment is managed with [Poetry](https://python-poetry.org/)
(2.2 or later). Exact versions of every tool, with hashes, are pinned in
`poetry.lock`. See [CONTRIBUTING.md](CONTRIBUTING.md) for full details. In short:

```bash
poetry sync                      # create the environment with the locked dev tools
poetry run pre-commit install    # optional: run checks on every commit

poetry run pytest                # run the tests
poetry run tox                   # every Python version + lowest/latest deps + lint + type + package checks
poetry run tox -e py313          # tests on one version
```

## Licence

[MIT](LICENSE)
