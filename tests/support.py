"""Typed helpers shared by the test modules."""

from __future__ import annotations

from typing import Protocol, cast

from faker import Faker

from faker_vedic_astrology_birth_chart import VedicAstrologyProvider
from faker_vedic_astrology_birth_chart.chart import BirthChart, PlanetPlacement
from faker_vedic_astrology_birth_chart.constants import RetrogradeFlag

__all__ = ["VedicFaker", "make_vedic_faker"]


class VedicFaker(Protocol):
    """Static type of a Faker instance with the Vedic provider added.

    Faker adds provider methods at runtime, so type checkers cannot see
    them. This protocol describes them so tests stay strictly typed.
    """

    def vedic_planet(self) -> str:
        """Return a random planet name."""

    def vedic_sign(self) -> str:
        """Return a random sign."""

    def vedic_nakshatra(self) -> str:
        """Return a random nakshatra."""

    def vedic_degree(self) -> float:
        """Return a random degree within a sign."""

    def vedic_ascendant(self) -> str:
        """Return a random ascendant sign."""

    def vedic_retrograde(self, planet: str) -> RetrogradeFlag:
        """Return a retrograde flag for a planet."""

    def vedic_planet_placement(
        self, planet: str | None = None, ascendant: str | None = None
    ) -> PlanetPlacement:
        """Return a single placement."""

    def vedic_birth_chart(
        self, ascendant: str | None = None, constrain_inner_planets: bool = True
    ) -> BirthChart:
        """Return a full chart."""


def make_vedic_faker(*locales: str) -> VedicFaker:
    """Create a Faker instance with the Vedic provider registered.

    Parameters
    ----------
    *locales : str
        Optional Faker locales, e.g. ``"hi_IN"``.

    Returns
    -------
    VedicFaker
        The Faker instance, typed so its ``vedic_*`` methods are visible.
    """
    instance = Faker(list(locales)) if locales else Faker()
    instance.add_provider(VedicAstrologyProvider)
    return cast(VedicFaker, instance)
