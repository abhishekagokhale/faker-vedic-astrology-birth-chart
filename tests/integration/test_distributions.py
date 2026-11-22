"""Integration tests on the statistical behaviour of many generated charts.

These tests use a large seeded sample (see the ``many_charts`` fixture) to
check that the data is realistic: retrograde rates match the empirical
figures, every value can occur, and repetitions are allowed where the
rules allow them.
"""

from __future__ import annotations

from collections import Counter

import pytest

from faker_vedic_astrology_birth_chart.chart import BirthChart
from faker_vedic_astrology_birth_chart.constants import (
    NAKSHATRAS,
    PLANETS,
    RETROGRADE_CYCLES,
    SIGNS,
)

#: Allowed absolute gap between observed and expected rates. With 20,000
#: charts the standard error is under 0.004, so this is a wide margin.
TOLERANCE = 0.02


@pytest.mark.parametrize("planet", PLANETS)
def test_retrograde_rate_matches_empirical_frequency(
    many_charts: list[BirthChart], planet: str
) -> None:
    """The share of charts with the planet retrograde is close to its empirical rate."""
    flags = [p["retrograde"] for chart in many_charts for p in chart if p["planet"] == planet]
    observed = flags.count("yes") / len(flags)
    assert observed == pytest.approx(RETROGRADE_CYCLES[planet].probability, abs=TOLERANCE)


def test_every_house_sign_and_nakshatra_occurs(many_charts: list[BirthChart]) -> None:
    """Across many charts, all 12 houses, 12 signs and 27 nakshatras appear."""
    placements = [p for chart in many_charts for p in chart]
    assert {p["house"] for p in placements} == set(range(1, 13))
    assert {p["sign"] for p in placements} == set(SIGNS)
    assert {p["nakshatra"] for p in placements} == set(NAKSHATRAS)


def test_degrees_cover_the_full_range(many_charts: list[BirthChart]) -> None:
    """Degrees span 0.0 to 29.9 at one-decimal resolution."""
    degrees = {p["degree"] for chart in many_charts for p in chart}
    assert min(degrees) == 0.0
    assert max(degrees) == 29.9
    assert len(degrees) == 300


def test_signs_and_houses_can_repeat_within_a_chart(many_charts: list[BirthChart]) -> None:
    """Planets often share a sign (conjunctions), so repeats occur in most charts."""
    with_repeat = sum(1 for chart in many_charts if len({p["sign"] for p in chart}) < 9)
    assert with_repeat / len(many_charts) > 0.5


def test_ascendants_are_roughly_uniform(many_charts: list[BirthChart]) -> None:
    """Each sign is the ascendant in roughly 1/12 of charts."""
    ascendants = Counter(
        next(
            SIGNS[(SIGNS.index(p["sign"]) - p["house"] + 1) % 12]
            for p in chart
            if p["planet"] == "Sun"
        )
        for chart in many_charts
    )
    for sign in SIGNS:
        assert ascendants[sign] / len(many_charts) == pytest.approx(1 / 12, abs=TOLERANCE)


def test_rahu_and_ketu_always_share_degree_and_sit_six_houses_apart(
    many_charts: list[BirthChart],
) -> None:
    """In every chart, Ketu has Rahu's degree and is in the seventh house from Rahu."""
    for chart in many_charts:
        rahu = next(p for p in chart if p["planet"] == "Rahu")
        ketu = next(p for p in chart if p["planet"] == "Ketu")
        assert rahu["degree"] == ketu["degree"]
        assert (ketu["house"] - rahu["house"]) % 12 == 6
