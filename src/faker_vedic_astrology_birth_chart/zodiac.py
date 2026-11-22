"""Pure functions for sidereal zodiac arithmetic.

These helpers convert between absolute ecliptic longitude, sign, degree,
nakshatra and house. They have no randomness and no side effects, so they
are easy to test and reuse on their own.

Notes
-----
Longitudes are integers in **tenths of a degree** in ``[0, 3600)``, so
``1234`` means 123.4 degrees, which is 3.4 degrees into Leo. Any integer
is accepted and wrapped round the zodiac.

Houses use the *whole-sign* system that is standard in Vedic astrology:
the ascendant's sign is house 1, the next sign is house 2, and so on.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType
from typing import Final

from faker_vedic_astrology_birth_chart.constants import (
    DEGREE_DECIMALS,
    DEGREES_PER_SIGN,
    NAKSHATRAS,
    NODE_SEPARATION_DEGREES,
    NUM_HOUSES,
    SIGNS,
    TENTHS_PER_DEGREE,
    TENTHS_PER_SIGN,
    TENTHS_PER_ZODIAC,
)

__all__ = [
    "SIGN_NAKSHATRA_MAP",
    "NakshatraSegment",
    "angular_distance",
    "degree_in_sign",
    "degree_to_tenths",
    "house_of_sign",
    "longitude_from_sign_degree",
    "nakshatra_of",
    "nakshatras_in_sign",
    "normalise",
    "opposite",
    "sign_index",
    "sign_of",
    "sign_of_house",
]

# One nakshatra is 400/3 tenths of a degree. Using integers (x * 3 // 400)
# keeps boundaries exact.
_NAKSHATRA_NUMERATOR: Final[int] = len(NAKSHATRAS)
_NAKSHATRA_DENOMINATOR: Final[int] = TENTHS_PER_ZODIAC


def normalise(longitude: int) -> int:
    """Wrap a longitude into the range ``[0, 3600)``.

    Parameters
    ----------
    longitude : int
        Longitude in tenths of a degree. May be negative or 3600 or more.

    Returns
    -------
    int
        The same position expressed in ``[0, 3600)``.

    Examples
    --------
    >>> normalise(3605)
    5
    >>> normalise(-10)
    3590
    """
    return longitude % TENTHS_PER_ZODIAC


def sign_index(sign: str) -> int:
    """Return the zero-based zodiac index of a sign name.

    Parameters
    ----------
    sign : str
        One of :data:`~faker_vedic_astrology_birth_chart.constants.SIGNS`.

    Returns
    -------
    int
        Index in ``[0, 12)``, where Aries is 0 and Pisces is 11.

    Raises
    ------
    ValueError
        If ``sign`` is not a known sign name.

    Examples
    --------
    >>> sign_index("Leo")
    4
    """
    try:
        return SIGNS.index(sign)
    except ValueError:
        raise ValueError(f"Unknown sign {sign!r}; expected one of {SIGNS}") from None


def degree_to_tenths(degree: float) -> int:
    """Convert a one-decimal degree value into integer tenths.

    Parameters
    ----------
    degree : float
        Degree value, e.g. ``12.3``.

    Returns
    -------
    int
        ``degree`` multiplied by ten and rounded to the nearest integer.

    Examples
    --------
    >>> degree_to_tenths(12.3)
    123
    """
    return round(degree * TENTHS_PER_DEGREE)


def sign_of(longitude: int) -> str:
    """Return the sign containing a longitude.

    Parameters
    ----------
    longitude : int
        Longitude in tenths of a degree.

    Returns
    -------
    str
        The sign name.

    Examples
    --------
    >>> sign_of(0)
    'Aries'
    >>> sign_of(3599)
    'Pisces'
    """
    return SIGNS[normalise(longitude) // TENTHS_PER_SIGN]


def degree_in_sign(longitude: int) -> float:
    """Return how far a longitude lies inside its sign.

    Parameters
    ----------
    longitude : int
        Longitude in tenths of a degree.

    Returns
    -------
    float
        Degree in ``[0.0, 30.0)`` with one decimal place.

    Examples
    --------
    >>> degree_in_sign(1234)
    3.4
    """
    tenths = normalise(longitude) % TENTHS_PER_SIGN
    return round(tenths / TENTHS_PER_DEGREE, DEGREE_DECIMALS)


def nakshatra_of(longitude: int) -> str:
    """Return the nakshatra containing a longitude.

    Parameters
    ----------
    longitude : int
        Longitude in tenths of a degree.

    Returns
    -------
    str
        The nakshatra name.

    Examples
    --------
    >>> nakshatra_of(0)
    'Ashvini'
    >>> nakshatra_of(400)  # exactly 40.0 degrees, the start of Rohini
    'Rohini'
    """
    index = normalise(longitude) * _NAKSHATRA_NUMERATOR // _NAKSHATRA_DENOMINATOR
    return NAKSHATRAS[index]


def longitude_from_sign_degree(sign: str, degree: float) -> int:
    """Combine a sign and a degree within it into an absolute longitude.

    Parameters
    ----------
    sign : str
        Sign name.
    degree : float
        Degree within the sign, in ``[0.0, 30.0)``.

    Returns
    -------
    int
        Longitude in tenths of a degree.

    Raises
    ------
    ValueError
        If ``sign`` is unknown or ``degree`` is outside ``[0.0, 30.0)``.

    Examples
    --------
    >>> longitude_from_sign_degree("Leo", 3.4)
    1234
    """
    if not 0 <= degree < DEGREES_PER_SIGN:
        raise ValueError(f"degree must be in [0, {DEGREES_PER_SIGN}), got {degree!r}")
    return sign_index(sign) * TENTHS_PER_SIGN + degree_to_tenths(degree)


def house_of_sign(sign: str, ascendant: str) -> int:
    """Return the whole-sign house number a sign occupies.

    Parameters
    ----------
    sign : str
        The sign whose house is wanted.
    ascendant : str
        The ascendant (lagna) sign, which is house 1.

    Returns
    -------
    int
        House number in ``[1, 12]``.

    Examples
    --------
    >>> house_of_sign("Leo", ascendant="Aries")
    5
    >>> house_of_sign("Aries", ascendant="Pisces")
    2
    """
    return (sign_index(sign) - sign_index(ascendant)) % NUM_HOUSES + 1


def sign_of_house(house: int, ascendant: str) -> str:
    """Return the sign that falls in a given whole-sign house.

    Parameters
    ----------
    house : int
        House number in ``[1, 12]``.
    ascendant : str
        The ascendant sign, which is house 1.

    Returns
    -------
    str
        The sign name.

    Raises
    ------
    ValueError
        If ``house`` is outside ``[1, 12]``.

    Examples
    --------
    >>> sign_of_house(7, ascendant="Aries")
    'Libra'
    """
    if not 1 <= house <= NUM_HOUSES:
        raise ValueError(f"house must be in [1, {NUM_HOUSES}], got {house!r}")
    return SIGNS[(sign_index(ascendant) + house - 1) % NUM_HOUSES]


def opposite(longitude: int) -> int:
    """Return the longitude exactly 180 degrees away.

    This is how Ketu is placed relative to Rahu.

    Parameters
    ----------
    longitude : int
        Longitude in tenths of a degree.

    Returns
    -------
    int
        Opposite longitude in ``[0, 3600)``.

    Examples
    --------
    >>> opposite(100)
    1900
    """
    return normalise(longitude + NODE_SEPARATION_DEGREES * TENTHS_PER_DEGREE)


def angular_distance(first: int, second: int) -> int:
    """Return the shortest distance between two longitudes.

    Parameters
    ----------
    first, second : int
        Longitudes in tenths of a degree.

    Returns
    -------
    int
        Separation in tenths of a degree, in ``[0, 1800]``.

    Examples
    --------
    >>> angular_distance(3590, 10)
    20
    """
    diff = normalise(first - second)
    return min(diff, TENTHS_PER_ZODIAC - diff)


@dataclass(frozen=True, slots=True)
class NakshatraSegment:
    """The part of a nakshatra that falls inside one sign.

    Parameters
    ----------
    nakshatra : str
        Nakshatra name.
    start_degree : float
        Degree within the sign where the segment starts (inclusive).
    end_degree : float
        Degree within the sign where the segment ends (exclusive).
    """

    nakshatra: str
    start_degree: float
    end_degree: float


def nakshatras_in_sign(sign: str) -> tuple[NakshatraSegment, ...]:
    """List the nakshatra segments that make up a sign.

    Every sign contains parts of either two or three nakshatras, because a
    sign is 30 degrees and a nakshatra is 13 degrees 20 minutes.

    Parameters
    ----------
    sign : str
        Sign name.

    Returns
    -------
    tuple of NakshatraSegment
        Segments in order. They are contiguous and together cover
        ``[0, 30)``.

    Examples
    --------
    >>> [s.nakshatra for s in nakshatras_in_sign("Aries")]
    ['Ashvini', 'Bharani', 'Krittika']
    """
    span = Fraction(360, len(NAKSHATRAS))
    sign_start = Fraction(sign_index(sign) * DEGREES_PER_SIGN)
    sign_end = sign_start + DEGREES_PER_SIGN
    segments: list[NakshatraSegment] = []
    for index, name in enumerate(NAKSHATRAS):
        start = max(index * span, sign_start)
        end = min((index + 1) * span, sign_end)
        if start < end:
            segments.append(
                NakshatraSegment(
                    nakshatra=name,
                    start_degree=float(start - sign_start),
                    end_degree=float(end - sign_start),
                )
            )
    return tuple(segments)


#: Read-only mapping of each sign to the nakshatra segments it contains,
#: with degree ranges in the sidereal system.
SIGN_NAKSHATRA_MAP: Final[MappingProxyType[str, tuple[NakshatraSegment, ...]]] = MappingProxyType(
    {sign: nakshatras_in_sign(sign) for sign in SIGNS}
)
