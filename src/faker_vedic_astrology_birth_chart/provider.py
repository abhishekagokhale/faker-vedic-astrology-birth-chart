"""Faker provider for synthetic Vedic astrology birth charts.

Examples
--------
>>> from faker import Faker
>>> from faker_vedic_astrology_birth_chart import VedicAstrologyProvider
>>> fake = Faker()
>>> fake.add_provider(VedicAstrologyProvider)
>>> Faker.seed(0)
>>> chart = fake.vedic_birth_chart()
>>> len(chart)
9
"""

from __future__ import annotations

import random

from faker.providers import BaseProvider

from faker_vedic_astrology_birth_chart.chart import (
    BirthChart,
    PlanetPlacement,
    draw_retrograde,
    generate_birth_chart,
    make_placement,
    random_longitude,
    resolve_ascendant,
)
from faker_vedic_astrology_birth_chart.constants import (
    DEGREE_DECIMALS,
    NAKSHATRAS,
    PLANETS,
    SIGNS,
    TENTHS_PER_DEGREE,
    TENTHS_PER_SIGN,
    RetrogradeFlag,
)

__all__ = ["VedicAstrologyProvider"]


class VedicAstrologyProvider(BaseProvider):
    """Generate realistic but synthetic Vedic (sidereal) birth-chart data.

    Intended for testing and development only. The output is random and
    must never be used for real consultations or predictions.

    All methods use Faker's shared random generator, so ``Faker.seed(n)``
    makes results reproducible.

    Examples
    --------
    >>> from faker import Faker
    >>> fake = Faker()
    >>> fake.add_provider(VedicAstrologyProvider)
    >>> fake.vedic_sign() in SIGNS
    True
    """

    @property
    def _rng(self) -> random.Random:
        """Faker's shared random generator, typed for static checking.

        Returns
        -------
        random.Random
            The generator that ``Faker.seed`` controls.
        """
        rng: random.Random = self.generator.random
        return rng

    def vedic_planet(self) -> str:
        """Return a random planet name.

        Returns
        -------
        str
            One of Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu,
            Ketu.
        """
        return self.random_element(PLANETS)

    def vedic_sign(self) -> str:
        """Return a random sidereal zodiac sign.

        Returns
        -------
        str
            One of the 12 signs, Aries to Pisces.
        """
        return self.random_element(SIGNS)

    def vedic_nakshatra(self) -> str:
        """Return a random nakshatra.

        Returns
        -------
        str
            One of the 27 nakshatras.
        """
        return self.random_element(NAKSHATRAS)

    def vedic_degree(self) -> float:
        """Return a random degree within a sign.

        Returns
        -------
        float
            Value in ``[0.0, 30.0)`` with one decimal place.
        """
        tenths = self._rng.randrange(TENTHS_PER_SIGN)
        return round(tenths / TENTHS_PER_DEGREE, DEGREE_DECIMALS)

    def vedic_ascendant(self) -> str:
        """Return a random ascendant (lagna) sign.

        Pass the result to :meth:`vedic_birth_chart` to know which sign
        is house 1.

        Returns
        -------
        str
            One of the 12 signs.
        """
        return resolve_ascendant(self._rng)

    def vedic_retrograde(self, planet: str) -> RetrogradeFlag:
        """Return a retrograde flag for a planet.

        Parameters
        ----------
        planet : str
            Planet name.

        Returns
        -------
        {"yes", "no"}
            Always ``"no"`` for Sun and Moon, always ``"yes"`` for Rahu and
            Ketu, otherwise weighted by how often the planet is retrograde.

        Raises
        ------
        ValueError
            If ``planet`` is not a known planet.
        """
        _require_planet(planet)
        return draw_retrograde(self._rng, planet)

    def vedic_planet_placement(
        self, planet: str | None = None, ascendant: str | None = None
    ) -> PlanetPlacement:
        """Return a single, stand-alone planet placement.

        The placement is drawn on its own, so cross-planet rules (such as
        Rahu and Ketu being opposite) do not apply. Use
        :meth:`vedic_birth_chart` for a full, consistent chart.

        Parameters
        ----------
        planet : str or None, optional
            Planet to place. Random if ``None``.
        ascendant : str or None, optional
            Ascendant sign used to work out the house. Random if ``None``.

        Returns
        -------
        PlanetPlacement
            Dictionary with keys planet, house, sign, nakshatra, degree and
            retrograde.

        Raises
        ------
        ValueError
            If ``planet`` or ``ascendant`` is not recognised.
        """
        rng = self._rng
        name = self.vedic_planet() if planet is None else _require_planet(planet)
        lagna = resolve_ascendant(rng, ascendant)
        return make_placement(name, random_longitude(rng), lagna, draw_retrograde(rng, name))

    def vedic_birth_chart(
        self, ascendant: str | None = None, constrain_inner_planets: bool = True
    ) -> BirthChart:
        """Return a complete synthetic birth chart.

        Parameters
        ----------
        ascendant : str or None, optional
            Ascendant sign (house 1). Random if ``None``.
        constrain_inner_planets : bool, default True
            Keep Mercury within 28 degrees and Venus within 47 degrees of
            the Sun, as in real skies.

        Returns
        -------
        BirthChart
            Tuple of nine dictionaries, one per planet, each with keys
            planet, house, sign, nakshatra, degree and retrograde.

        Raises
        ------
        ValueError
            If ``ascendant`` is not a known sign.

        Examples
        --------
        >>> from faker import Faker
        >>> fake = Faker()
        >>> fake.add_provider(VedicAstrologyProvider)
        >>> chart = fake.vedic_birth_chart(ascendant="Leo")
        >>> sorted(chart[0])
        ['degree', 'house', 'nakshatra', 'planet', 'retrograde', 'sign']
        """
        return generate_birth_chart(
            self._rng,
            ascendant=ascendant,
            constrain_inner_planets=constrain_inner_planets,
        )


def _require_planet(planet: str) -> str:
    """Return ``planet`` unchanged if it is a known planet.

    Parameters
    ----------
    planet : str
        Planet name to check.

    Returns
    -------
    str
        The same planet name.

    Raises
    ------
    ValueError
        If ``planet`` is not one of the nine planets.
    """
    if planet not in PLANETS:
        raise ValueError(f"Unknown planet {planet!r}; expected one of {PLANETS}")
    return planet
