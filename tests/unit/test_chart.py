"""Unit tests for chart building in :mod:`faker_vedic_astrology_birth_chart.chart`.

These tests check each random building block and the structure of a
single generated chart, using a seeded :class:`random.Random`.
"""

from __future__ import annotations

import random

import pytest

from faker_vedic_astrology_birth_chart.chart import (
    PLACEMENT_KEYS,
    draw_longitudes,
    draw_retrograde,
    generate_birth_chart,
    make_placement,
    random_longitude,
    random_longitude_near,
    resolve_ascendant,
)
from faker_vedic_astrology_birth_chart.constants import PLANETS, SIGNS
from faker_vedic_astrology_birth_chart.zodiac import angular_distance, opposite


def test_resolve_ascendant_keeps_a_given_sign(rng: random.Random) -> None:
    """A valid ascendant passed in is returned unchanged."""
    assert resolve_ascendant(rng, "Scorpio") == "Scorpio"


def test_resolve_ascendant_draws_a_sign_when_none(rng: random.Random) -> None:
    """With no ascendant given, a valid sign is drawn."""
    assert resolve_ascendant(rng) in SIGNS


def test_resolve_ascendant_rejects_unknown_sign(rng: random.Random) -> None:
    """An unknown ascendant raises ValueError."""
    with pytest.raises(ValueError, match="Unknown sign"):
        resolve_ascendant(rng, "Arise")


def test_random_longitude_stays_in_range(rng: random.Random) -> None:
    """Random longitudes always fall in [0, 3600)."""
    values = [random_longitude(rng) for _ in range(5_000)]
    assert min(values) >= 0
    assert max(values) < 3600


@pytest.mark.parametrize("centre", [0, 50, 1800, 3590])
def test_random_longitude_near_respects_limit(rng: random.Random, centre: int) -> None:
    """Longitudes drawn near a point are never further than the limit, even across 0 degrees."""
    for _ in range(2_000):
        value = random_longitude_near(rng, centre, max_degrees=28)
        assert 0 <= value < 3600
        assert angular_distance(value, centre) <= 280


@pytest.mark.parametrize(("planet", "flag"), [("Sun", "no"), ("Moon", "no")])
def test_draw_retrograde_never_for_luminaries(rng: random.Random, planet: str, flag: str) -> None:
    """Sun and Moon always get retrograde 'no'."""
    assert {draw_retrograde(rng, planet) for _ in range(500)} == {flag}


@pytest.mark.parametrize("planet", ["Rahu", "Ketu"])
def test_draw_retrograde_always_for_nodes(rng: random.Random, planet: str) -> None:
    """Rahu and Ketu always get retrograde 'yes'."""
    assert {draw_retrograde(rng, planet) for _ in range(500)} == {"yes"}


@pytest.mark.parametrize("planet", ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"])
def test_draw_retrograde_varies_for_other_planets(rng: random.Random, planet: str) -> None:
    """The other planets can be either retrograde or direct."""
    assert {draw_retrograde(rng, planet) for _ in range(2_000)} == {"yes", "no"}


def test_draw_retrograde_rejects_unknown_planet(rng: random.Random) -> None:
    """An unknown planet raises KeyError."""
    with pytest.raises(KeyError):
        draw_retrograde(rng, "Pluto")


def test_draw_longitudes_places_every_planet(rng: random.Random) -> None:
    """A longitude is drawn for each of the nine planets."""
    assert set(draw_longitudes(rng)) == set(PLANETS)


def test_draw_longitudes_puts_ketu_opposite_rahu(rng: random.Random) -> None:
    """Ketu's longitude is always Rahu's plus 180 degrees."""
    for _ in range(500):
        longitudes = draw_longitudes(rng)
        assert longitudes["Ketu"] == opposite(longitudes["Rahu"])


def test_draw_longitudes_can_leave_inner_planets_unconstrained() -> None:
    """With the constraint off, Mercury is sometimes far from the Sun."""
    generator = random.Random(1)
    distances = [
        angular_distance(lon["Mercury"], lon["Sun"])
        for lon in (draw_longitudes(generator, constrain_inner_planets=False) for _ in range(500))
    ]
    assert max(distances) > 280


def test_make_placement_derives_all_fields() -> None:
    """A placement's sign, degree, nakshatra and house all come from the longitude."""
    placement = make_placement("Moon", 1234, ascendant="Aries", retrograde="no")
    assert placement == {
        "planet": "Moon",
        "house": 5,
        "sign": "Leo",
        "nakshatra": "Magha",
        "degree": 3.4,
        "retrograde": "no",
    }


def test_generate_birth_chart_shape(rng: random.Random) -> None:
    """A chart is a tuple of nine dicts, one per planet, each with the six required keys."""
    chart = generate_birth_chart(rng)
    assert isinstance(chart, tuple)
    assert len(chart) == 9
    assert [p["planet"] for p in chart] == list(PLANETS)
    for placement in chart:
        assert isinstance(placement, dict)
        assert tuple(placement) == PLACEMENT_KEYS


def test_generate_birth_chart_respects_given_ascendant(rng: random.Random) -> None:
    """When an ascendant is given, any planet in that sign is in house 1."""
    for _ in range(200):
        for placement in generate_birth_chart(rng, ascendant="Virgo"):
            assert (placement["house"] == 1) == (placement["sign"] == "Virgo")


def test_generate_birth_chart_is_reproducible() -> None:
    """The same seed always produces the same chart."""
    assert generate_birth_chart(random.Random(42)) == generate_birth_chart(random.Random(42))


def test_generate_birth_chart_varies_between_draws(rng: random.Random) -> None:
    """Consecutive charts from one generator are different."""
    assert generate_birth_chart(rng) != generate_birth_chart(rng)
