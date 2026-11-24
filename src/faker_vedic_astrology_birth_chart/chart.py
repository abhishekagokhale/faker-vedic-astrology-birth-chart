"""Build and validate synthetic Vedic birth charts.

The generator works in three steps:

1. Fix the ascendant (lagna) sign. This is house 1.
2. Draw an absolute sidereal longitude for each planet. Ketu is never
   drawn: it is always placed exactly opposite Rahu. Mercury and Venus are,
   by default, kept within their real maximum distance from the Sun.
3. Derive sign, degree, nakshatra and house from each longitude, then draw
   the retrograde flag using empirical frequencies.

Because sign, degree and nakshatra all come from one longitude, they always
agree with each other. Because houses come from signs, every chart is
consistent with a single ascendant.

All randomness comes from a :class:`random.Random` passed in by the caller,
so results are reproducible when the caller seeds it.
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from typing import Final, TypedDict, cast

from faker_vedic_astrology_birth_chart.constants import (
    ALWAYS_RETROGRADE,
    DEGREE_DECIMALS,
    DEGREES_PER_SIGN,
    MAX_ELONGATION_FROM_SUN,
    NAKSHATRAS,
    NEVER_RETROGRADE,
    NUM_HOUSES,
    PLANETS,
    RETROGRADE_CYCLES,
    RETROGRADE_NO,
    RETROGRADE_YES,
    SIGNS,
    TENTHS_PER_DEGREE,
    TENTHS_PER_ZODIAC,
    RetrogradeFlag,
)
from faker_vedic_astrology_birth_chart.zodiac import (
    angular_distance,
    degree_in_sign,
    house_of_sign,
    longitude_from_sign_degree,
    nakshatra_of,
    normalise,
    opposite,
    sign_index,
    sign_of,
)

__all__ = [
    "PLACEMENT_KEYS",
    "BirthChart",
    "InvalidBirthChartError",
    "PlanetPlacement",
    "draw_longitudes",
    "draw_retrograde",
    "generate_birth_chart",
    "make_placement",
    "random_longitude",
    "random_longitude_near",
    "resolve_ascendant",
    "validate_birth_chart",
    "validate_placement",
]


class PlanetPlacement(TypedDict):
    """One planet's position in a birth chart.

    Attributes
    ----------
    planet : str
        One of the nine planets.
    house : int
        Whole-sign house number in ``[1, 12]``.
    sign : str
        One of the 12 sidereal signs.
    nakshatra : str
        One of the 27 nakshatras. Always consistent with ``sign`` and
        ``degree``.
    degree : float
        Degree within the sign, one decimal place, in ``[0.0, 30.0)``.
    retrograde : {"yes", "no"}
        Whether the planet is retrograde.
    """

    planet: str
    house: int
    sign: str
    nakshatra: str
    degree: float
    retrograde: RetrogradeFlag


#: A birth chart: exactly nine placements, one per planet.
BirthChart = tuple[PlanetPlacement, ...]

#: The keys every placement must have, in output order.
PLACEMENT_KEYS: Final[tuple[str, ...]] = (
    "planet",
    "house",
    "sign",
    "nakshatra",
    "degree",
    "retrograde",
)


class InvalidBirthChartError(ValueError):
    """Raised when a birth chart breaks one of the Vedic chart rules."""


# ---------------------------------------------------------------------------
# Random building blocks
# ---------------------------------------------------------------------------


def resolve_ascendant(rng: random.Random, ascendant: str | None = None) -> str:
    """Return the given ascendant, or draw one at random.

    Parameters
    ----------
    rng : random.Random
        Source of randomness.
    ascendant : str or None, optional
        Ascendant sign to use. If ``None`` (the default), one of the 12
        signs is chosen uniformly.

    Returns
    -------
    str
        The ascendant sign.

    Raises
    ------
    ValueError
        If ``ascendant`` is given but is not a known sign.
    """
    if ascendant is None:
        return rng.choice(SIGNS)
    sign_index(ascendant)  # raises ValueError for unknown signs
    return ascendant


def random_longitude(rng: random.Random) -> int:
    """Draw a uniformly random longitude.

    Parameters
    ----------
    rng : random.Random
        Source of randomness.

    Returns
    -------
    int
        Longitude in tenths of a degree, in ``[0, 3600)``.
    """
    return rng.randrange(TENTHS_PER_ZODIAC)


def random_longitude_near(rng: random.Random, centre: int, max_degrees: int) -> int:
    """Draw a random longitude within a set distance of another.

    Parameters
    ----------
    rng : random.Random
        Source of randomness.
    centre : int
        Longitude (tenths of a degree) to stay close to.
    max_degrees : int
        Maximum distance from ``centre`` in whole degrees, inclusive.

    Returns
    -------
    int
        Longitude in ``[0, 3600)`` no more than ``max_degrees`` from
        ``centre``.
    """
    limit = max_degrees * TENTHS_PER_DEGREE
    return normalise(centre + rng.randint(-limit, limit))


def draw_retrograde(rng: random.Random, planet: str) -> RetrogradeFlag:
    """Draw a retrograde flag for a planet using empirical frequencies.

    Sun and Moon are always ``"no"``; Rahu and Ketu are always ``"yes"``.
    For other planets the chance of ``"yes"`` equals the share of time the
    planet is retrograde (see
    :data:`~faker_vedic_astrology_birth_chart.constants.RETROGRADE_CYCLES`).

    Parameters
    ----------
    rng : random.Random
        Source of randomness. Not used for the fixed planets.
    planet : str
        Planet name.

    Returns
    -------
    {"yes", "no"}
        The retrograde flag.

    Raises
    ------
    KeyError
        If ``planet`` is not a known planet.
    """
    if planet in NEVER_RETROGRADE:
        return RETROGRADE_NO
    if planet in ALWAYS_RETROGRADE:
        return RETROGRADE_YES
    probability = RETROGRADE_CYCLES[planet].probability
    return RETROGRADE_YES if rng.random() < probability else RETROGRADE_NO


def draw_longitudes(rng: random.Random, *, constrain_inner_planets: bool = True) -> dict[str, int]:
    """Draw a longitude for each of the nine planets.

    Parameters
    ----------
    rng : random.Random
        Source of randomness.
    constrain_inner_planets : bool, default True
        If ``True``, Mercury and Venus are kept within their maximum
        distance from the Sun (28 and 47 degrees). If ``False``, they are
        placed uniformly like the other planets.

    Returns
    -------
    dict of {str: int}
        Planet name to longitude in tenths of a degree. Ketu is always
        exactly opposite Rahu.
    """
    longitudes: dict[str, int] = {}
    for planet in PLANETS:
        if planet == "Ketu":
            continue
        if constrain_inner_planets and planet in MAX_ELONGATION_FROM_SUN:
            longitudes[planet] = random_longitude_near(
                rng, longitudes["Sun"], MAX_ELONGATION_FROM_SUN[planet]
            )
        else:
            longitudes[planet] = random_longitude(rng)
    longitudes["Ketu"] = opposite(longitudes["Rahu"])
    return longitudes


def make_placement(
    planet: str, longitude: int, ascendant: str, retrograde: RetrogradeFlag
) -> PlanetPlacement:
    """Build a placement dictionary from a longitude.

    Parameters
    ----------
    planet : str
        Planet name.
    longitude : int
        Longitude in tenths of a degree.
    ascendant : str
        Ascendant sign, used to work out the house.
    retrograde : {"yes", "no"}
        Retrograde flag.

    Returns
    -------
    PlanetPlacement
        Dictionary with exactly the keys in :data:`PLACEMENT_KEYS`.
    """
    sign = sign_of(longitude)
    return PlanetPlacement(
        planet=planet,
        house=house_of_sign(sign, ascendant),
        sign=sign,
        nakshatra=nakshatra_of(longitude),
        degree=degree_in_sign(longitude),
        retrograde=retrograde,
    )


def generate_birth_chart(
    rng: random.Random,
    *,
    ascendant: str | None = None,
    constrain_inner_planets: bool = True,
) -> BirthChart:
    """Generate one synthetic birth chart.

    Parameters
    ----------
    rng : random.Random
        Source of randomness.
    ascendant : str or None, optional
        Ascendant sign (house 1). Drawn at random if ``None``.
    constrain_inner_planets : bool, default True
        Keep Mercury and Venus near the Sun, as in real skies.

    Returns
    -------
    BirthChart
        Tuple of nine placements, one per planet, in the order of
        :data:`~faker_vedic_astrology_birth_chart.constants.PLANETS`.

    Raises
    ------
    ValueError
        If ``ascendant`` is not a known sign.
    """
    lagna = resolve_ascendant(rng, ascendant)
    longitudes = draw_longitudes(rng, constrain_inner_planets=constrain_inner_planets)
    return tuple(
        make_placement(planet, longitudes[planet], lagna, draw_retrograde(rng, planet))
        for planet in PLANETS
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _check(condition: bool, message: str) -> None:
    """Raise :class:`InvalidBirthChartError` when ``condition`` is false.

    Parameters
    ----------
    condition : bool
        The rule being checked.
    message : str
        Error message to use if the rule fails.

    Raises
    ------
    InvalidBirthChartError
        If ``condition`` is false.
    """
    if not condition:
        raise InvalidBirthChartError(message)


def validate_placement(placement: Mapping[str, object]) -> None:
    """Check that a single placement follows every per-planet rule.

    Parameters
    ----------
    placement : Mapping
        A placement dictionary.

    Raises
    ------
    InvalidBirthChartError
        If keys, types or values are wrong, the nakshatra does not match the
        sign and degree, or the retrograde flag breaks a fixed rule.
    """
    _check(
        set(placement) == set(PLACEMENT_KEYS),
        f"placement keys must be {PLACEMENT_KEYS}, got {tuple(placement)}",
    )
    planet = placement["planet"]
    house = placement["house"]
    sign = placement["sign"]
    nakshatra = placement["nakshatra"]
    degree = placement["degree"]
    retrograde = placement["retrograde"]

    _check(planet in PLANETS, f"unknown planet {planet!r}")
    _check(
        isinstance(house, int) and not isinstance(house, bool) and 1 <= house <= NUM_HOUSES,
        f"{planet}: house must be an int in [1, {NUM_HOUSES}], got {house!r}",
    )
    _check(sign in SIGNS, f"{planet}: unknown sign {sign!r}")
    _check(nakshatra in NAKSHATRAS, f"{planet}: unknown nakshatra {nakshatra!r}")
    _check(
        isinstance(degree, float)
        and 0.0 <= degree < DEGREES_PER_SIGN
        and round(degree, DEGREE_DECIMALS) == degree,
        f"{planet}: degree must be a one-decimal float in [0.0, 30.0), got {degree!r}",
    )
    _check(
        retrograde in (RETROGRADE_YES, RETROGRADE_NO),
        f"{planet}: retrograde must be 'yes' or 'no', got {retrograde!r}",
    )
    if planet in NEVER_RETROGRADE:
        _check(retrograde == RETROGRADE_NO, f"{planet} can never be retrograde")
    if planet in ALWAYS_RETROGRADE:
        _check(retrograde == RETROGRADE_YES, f"{planet} is always retrograde")

    # sign and degree were type-checked above, so the casts are safe.
    expected = nakshatra_of(longitude_from_sign_degree(cast(str, sign), cast(float, degree)))
    _check(
        nakshatra == expected,
        f"{planet}: {degree} {sign} lies in {expected}, not {nakshatra!r}",
    )


def validate_birth_chart(
    chart: Sequence[Mapping[str, object]],
    *,
    ascendant: str | None = None,
    constrain_inner_planets: bool = False,
) -> str:
    """Check that a birth chart follows every Vedic chart rule.

    Parameters
    ----------
    chart : Sequence of Mapping
        The chart to check.
    ascendant : str or None, optional
        If given, also check that this sign is house 1.
    constrain_inner_planets : bool, default False
        If ``True``, also check that Mercury and Venus are within their
        maximum distance from the Sun.

    Returns
    -------
    str
        The ascendant sign implied by the houses.

    Raises
    ------
    InvalidBirthChartError
        If any rule is broken.

    Examples
    --------
    >>> import random
    >>> chart = generate_birth_chart(random.Random(1), ascendant="Leo")
    >>> validate_birth_chart(chart)
    'Leo'
    """
    _check(isinstance(chart, tuple), f"chart must be a tuple, got {type(chart).__name__}")
    _check(len(chart) == len(PLANETS), f"chart must have {len(PLANETS)} placements")
    for placement in chart:
        validate_placement(placement)
    # Every placement has now been checked, so it is safe to treat them as typed.
    placements = [cast(PlanetPlacement, p) for p in chart]

    by_planet = {p["planet"]: p for p in placements}
    _check(set(by_planet) == set(PLANETS), "each planet must appear exactly once")

    implied = {(sign_index(p["sign"]) - p["house"] + 1) % NUM_HOUSES for p in placements}
    _check(len(implied) == 1, "houses and signs must agree with a single ascendant")
    lagna = SIGNS[implied.pop()]
    if ascendant is not None:
        _check(lagna == ascendant, f"house 1 is {lagna}, expected {ascendant}")

    longitudes = {
        planet: longitude_from_sign_degree(p["sign"], p["degree"])
        for planet, p in by_planet.items()
    }
    _check(
        longitudes["Ketu"] == opposite(longitudes["Rahu"]),
        "Rahu and Ketu must be exactly 180 degrees apart",
    )
    if constrain_inner_planets:
        for planet, max_degrees in MAX_ELONGATION_FROM_SUN.items():
            distance = angular_distance(longitudes[planet], longitudes["Sun"])
            _check(
                distance <= max_degrees * TENTHS_PER_DEGREE,
                f"{planet} must be within {max_degrees} degrees of the Sun",
            )
    return lagna
