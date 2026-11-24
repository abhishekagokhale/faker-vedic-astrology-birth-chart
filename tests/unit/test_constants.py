"""Unit tests for :mod:`faker_vedic_astrology_birth_chart.constants`.

These tests check the reference data itself: counts, uniqueness and the
retrograde frequencies derived from the empirical figures.
"""

from __future__ import annotations

import pytest

from faker_vedic_astrology_birth_chart.constants import (
    ALWAYS_RETROGRADE,
    MAX_ELONGATION_FROM_SUN,
    NAKSHATRAS,
    NEVER_RETROGRADE,
    PLANETS,
    RETROGRADE_CYCLES,
    SIGNS,
    TENTHS_PER_ZODIAC,
    RetrogradeCycle,
)


def test_there_are_nine_unique_planets() -> None:
    """The chart uses exactly nine distinct planets, including both nodes."""
    assert len(PLANETS) == 9
    assert len(set(PLANETS)) == 9
    assert {"Rahu", "Ketu", "Sun", "Moon"} <= set(PLANETS)


def test_there_are_twelve_unique_signs_starting_at_aries() -> None:
    """There are 12 distinct signs, in zodiacal order from Aries to Pisces."""
    assert len(SIGNS) == 12
    assert len(set(SIGNS)) == 12
    assert SIGNS[0] == "Aries"
    assert SIGNS[-1] == "Pisces"


def test_there_are_twenty_seven_unique_nakshatras() -> None:
    """There are 27 distinct nakshatras, from Ashvini to Revati."""
    assert len(NAKSHATRAS) == 27
    assert len(set(NAKSHATRAS)) == 27
    assert NAKSHATRAS[0] == "Ashvini"
    assert NAKSHATRAS[-1] == "Revati"


def test_zodiac_resolution_is_tenths_of_a_degree() -> None:
    """The full zodiac is 3600 internal units (360.0 degrees in tenths)."""
    assert TENTHS_PER_ZODIAC == 3600


def test_every_planet_has_a_retrograde_cycle() -> None:
    """Each planet has exactly one retrograde frequency entry."""
    assert set(RETROGRADE_CYCLES) == set(PLANETS)


@pytest.mark.parametrize("planet", sorted(NEVER_RETROGRADE))
def test_luminaries_have_zero_retrograde_probability(planet: str) -> None:
    """Sun and Moon are never retrograde, so their probability is 0."""
    assert RETROGRADE_CYCLES[planet].probability == 0


@pytest.mark.parametrize("planet", sorted(ALWAYS_RETROGRADE))
def test_nodes_have_full_retrograde_probability(planet: str) -> None:
    """Rahu and Ketu are always retrograde, so their probability is 1."""
    assert RETROGRADE_CYCLES[planet].probability == 1


@pytest.mark.parametrize(
    ("planet", "expected"),
    [
        ("Saturn", 140 / 365),
        ("Jupiter", 120 / 365),
        ("Mercury", 67.5 / 365),
        ("Venus", 41 / (18.5 * 365.25 / 12)),
        ("Mars", 76 / (25 * 365.25 / 12)),
    ],
)
def test_retrograde_probabilities_match_empirical_figures(planet: str, expected: float) -> None:
    """Each planet's probability equals retrograde days divided by cycle days."""
    assert RETROGRADE_CYCLES[planet].probability == pytest.approx(expected)


def test_retrograde_probabilities_are_ordered_as_expected() -> None:
    """Saturn is retrograde most often, then Jupiter, Mercury, Mars and Venus."""
    p = {name: cycle.probability for name, cycle in RETROGRADE_CYCLES.items()}
    assert p["Saturn"] > p["Jupiter"] > p["Mercury"] > p["Mars"] > p["Venus"] > 0


@pytest.mark.parametrize(
    ("retrograde_days", "cycle_days"),
    [(10, 0), (10, -5), (-1, 365), (400, 365)],
)
def test_retrograde_cycle_rejects_impossible_values(
    retrograde_days: float, cycle_days: float
) -> None:
    """A cycle with non-positive length or out-of-range days raises ValueError."""
    with pytest.raises(ValueError, match="must be"):
        RetrogradeCycle(retrograde_days=retrograde_days, cycle_days=cycle_days)


def test_fixed_retrograde_sets_do_not_overlap() -> None:
    """No planet can be both always and never retrograde."""
    assert not NEVER_RETROGRADE & ALWAYS_RETROGRADE


def test_inner_planet_elongation_limits() -> None:
    """Mercury stays within 28 degrees and Venus within 47 degrees of the Sun."""
    assert dict(MAX_ELONGATION_FROM_SUN) == {"Mercury": 28, "Venus": 47}
