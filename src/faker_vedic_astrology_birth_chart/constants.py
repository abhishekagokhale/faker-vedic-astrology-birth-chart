"""Reference data for the Vedic (sidereal) astrology birth-chart provider.

Everything in this module is static, immutable data. It is the single
source of truth for planets, signs, nakshatras, retrograde frequencies
and the other fixed values the generator relies on.

Notes
-----
Positions are handled internally in **tenths of a degree** (integers),
so a full zodiac of 360.0 degrees is ``3600`` units. Each sign is
``300`` units and each nakshatra is 13 degrees 20 minutes, i.e.
``400 / 3`` units. Integer arithmetic avoids floating-point drift at
sign and nakshatra boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Literal

__all__ = [
    "ALWAYS_RETROGRADE",
    "DAYS_PER_MONTH",
    "DEGREES_PER_SIGN",
    "DEGREE_DECIMALS",
    "MAX_ELONGATION_FROM_SUN",
    "NAKSHATRAS",
    "NAKSHATRA_SPAN_DEGREES",
    "NEVER_RETROGRADE",
    "NODE_SEPARATION_DEGREES",
    "NUM_HOUSES",
    "PLANETS",
    "RETROGRADE_CYCLES",
    "RETROGRADE_NO",
    "RETROGRADE_YES",
    "SIGNS",
    "TENTHS_PER_DEGREE",
    "TENTHS_PER_SIGN",
    "TENTHS_PER_ZODIAC",
    "RetrogradeCycle",
    "RetrogradeFlag",
]

# ---------------------------------------------------------------------------
# Planets (grahas)
# ---------------------------------------------------------------------------

#: The nine grahas used in a Vedic birth chart, in traditional weekday order
#: followed by the two lunar nodes.
PLANETS: Final[tuple[str, ...]] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)

# ---------------------------------------------------------------------------
# Signs (rashis) and houses
# ---------------------------------------------------------------------------

#: The 12 sidereal zodiac signs in zodiacal order, starting at 0 degrees
#: sidereal Aries (Mesha).
SIGNS: Final[tuple[str, ...]] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

#: Number of houses (bhavas) in a chart.
NUM_HOUSES: Final[int] = 12

#: Width of one sign in degrees.
DEGREES_PER_SIGN: Final[int] = 30

#: Degrees are reported to this many decimal places.
DEGREE_DECIMALS: Final[int] = 1

#: Internal resolution: one unit is a tenth of a degree.
TENTHS_PER_DEGREE: Final[int] = 10

#: Width of one sign in tenths of a degree.
TENTHS_PER_SIGN: Final[int] = DEGREES_PER_SIGN * TENTHS_PER_DEGREE

#: Full zodiac (360 degrees) in tenths of a degree.
TENTHS_PER_ZODIAC: Final[int] = TENTHS_PER_SIGN * len(SIGNS)

# ---------------------------------------------------------------------------
# Nakshatras (lunar mansions)
# ---------------------------------------------------------------------------

#: The 27 nakshatras in order from 0 degrees sidereal Aries. Spellings follow
#: https://en.wikipedia.org/wiki/List_of_Nakshatras.
NAKSHATRAS: Final[tuple[str, ...]] = (
    "Ashvini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashirsha",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)

#: Width of a nakshatra in degrees (13 degrees 20 minutes).
NAKSHATRA_SPAN_DEGREES: Final[float] = 360 / len(NAKSHATRAS)

# ---------------------------------------------------------------------------
# Lunar nodes and inner planets
# ---------------------------------------------------------------------------

#: Rahu and Ketu are always exactly opposite each other.
NODE_SEPARATION_DEGREES: Final[int] = 180

#: Maximum angular distance (degrees) that Mercury and Venus can be from the
#: Sun as seen from Earth (their greatest elongations, rounded up).
MAX_ELONGATION_FROM_SUN: Final[MappingProxyType[str, int]] = MappingProxyType(
    {"Mercury": 28, "Venus": 47}
)

# ---------------------------------------------------------------------------
# Retrograde motion
# ---------------------------------------------------------------------------

#: Allowed values for the ``retrograde`` key.
RetrogradeFlag = Literal["yes", "no"]
RETROGRADE_YES: Final[RetrogradeFlag] = "yes"
RETROGRADE_NO: Final[RetrogradeFlag] = "no"

#: Average length of a month in days (365.25 / 12), used to convert the
#: month-based cycles of Venus and Mars into days.
DAYS_PER_MONTH: Final[float] = 365.25 / 12


@dataclass(frozen=True, slots=True)
class RetrogradeCycle:
    """Empirical retrograde frequency of a planet.

    Parameters
    ----------
    retrograde_days : float
        Average number of days the planet spends retrograde per cycle.
    cycle_days : float
        Length of the observation cycle in days.

    Raises
    ------
    ValueError
        If ``cycle_days`` is not positive or ``retrograde_days`` lies
        outside ``[0, cycle_days]``.

    Examples
    --------
    >>> RetrogradeCycle(retrograde_days=140, cycle_days=365).probability
    0.3835616438356164
    """

    retrograde_days: float
    cycle_days: float

    def __post_init__(self) -> None:
        """Validate the cycle values."""
        if self.cycle_days <= 0:
            raise ValueError("cycle_days must be positive")
        if not 0 <= self.retrograde_days <= self.cycle_days:
            raise ValueError("retrograde_days must be between 0 and cycle_days")

    @property
    def probability(self) -> float:
        """Probability that the planet is retrograde on a random day.

        Returns
        -------
        float
            ``retrograde_days / cycle_days``, a value in ``[0, 1]``.
        """
        return self.retrograde_days / self.cycle_days


#: Empirical retrograde frequencies. Where a range was given the midpoint is
#: used (e.g. Mercury 63-72 days -> 67.5; Venus 40-42 days every 18-19 months
#: -> 41 days every 18.5 months; Mars 72-80 days every 24-26 months -> 76 days
#: every 25 months).
RETROGRADE_CYCLES: Final[MappingProxyType[str, RetrogradeCycle]] = MappingProxyType(
    {
        "Sun": RetrogradeCycle(retrograde_days=0, cycle_days=365),
        "Moon": RetrogradeCycle(retrograde_days=0, cycle_days=365),
        "Mars": RetrogradeCycle(retrograde_days=76, cycle_days=25 * DAYS_PER_MONTH),
        "Mercury": RetrogradeCycle(retrograde_days=67.5, cycle_days=365),
        "Jupiter": RetrogradeCycle(retrograde_days=120, cycle_days=365),
        "Venus": RetrogradeCycle(retrograde_days=41, cycle_days=18.5 * DAYS_PER_MONTH),
        "Saturn": RetrogradeCycle(retrograde_days=140, cycle_days=365),
        "Rahu": RetrogradeCycle(retrograde_days=365, cycle_days=365),
        "Ketu": RetrogradeCycle(retrograde_days=365, cycle_days=365),
    }
)

#: Planets that are never retrograde.
NEVER_RETROGRADE: Final[frozenset[str]] = frozenset({"Sun", "Moon"})

#: Planets that are always retrograde.
ALWAYS_RETROGRADE: Final[frozenset[str]] = frozenset({"Rahu", "Ketu"})
