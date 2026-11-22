"""Faker community provider for synthetic Vedic astrology birth charts.

For testing and development only. The data is random and must never be used
for real consultations or predictions.

Examples
--------
>>> from faker import Faker
>>> from faker_vedic_astrology_birth_chart import VedicAstrologyProvider
>>> fake = Faker()
>>> fake.add_provider(VedicAstrologyProvider)
>>> chart = fake.vedic_birth_chart()
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from faker_vedic_astrology_birth_chart.chart import (
    BirthChart,
    InvalidBirthChartError,
    PlanetPlacement,
    validate_birth_chart,
)
from faker_vedic_astrology_birth_chart.constants import NAKSHATRAS, PLANETS, SIGNS
from faker_vedic_astrology_birth_chart.provider import VedicAstrologyProvider
from faker_vedic_astrology_birth_chart.zodiac import SIGN_NAKSHATRA_MAP

try:
    __version__ = version("faker-vedic-astrology-birth-chart")
except PackageNotFoundError:  # pragma: no cover - only when running from a raw checkout
    __version__ = "0.0.0"

#: Alias so the provider can be imported with Faker's usual ``Provider`` name.
Provider = VedicAstrologyProvider

__all__ = [
    "NAKSHATRAS",
    "PLANETS",
    "SIGNS",
    "SIGN_NAKSHATRA_MAP",
    "BirthChart",
    "InvalidBirthChartError",
    "PlanetPlacement",
    "Provider",
    "VedicAstrologyProvider",
    "__version__",
    "validate_birth_chart",
]
