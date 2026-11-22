"""Unit tests for :mod:`faker_vedic_astrology_birth_chart.zodiac`.

These tests cover the pure conversion functions, with particular care at
boundaries: 0 degrees, the last tenth of a sign, nakshatra edges and the
wrap from Pisces back to Aries.
"""

from __future__ import annotations

from itertools import pairwise

import pytest

from faker_vedic_astrology_birth_chart.constants import NAKSHATRAS, SIGNS
from faker_vedic_astrology_birth_chart.zodiac import (
    SIGN_NAKSHATRA_MAP,
    angular_distance,
    degree_in_sign,
    degree_to_tenths,
    house_of_sign,
    longitude_from_sign_degree,
    nakshatra_of,
    nakshatras_in_sign,
    normalise,
    opposite,
    sign_index,
    sign_of,
    sign_of_house,
)


@pytest.mark.parametrize(
    ("longitude", "expected"),
    [(0, 0), (3599, 3599), (3600, 0), (3605, 5), (-1, 3599), (-3600, 0)],
)
def test_normalise_wraps_into_zodiac_range(longitude: int, expected: int) -> None:
    """Any integer longitude is wrapped into [0, 3600)."""
    assert normalise(longitude) == expected


def test_sign_index_returns_zodiac_position() -> None:
    """Each sign's index matches its position, Aries=0 to Pisces=11."""
    assert [sign_index(s) for s in SIGNS] == list(range(12))


def test_sign_index_rejects_unknown_sign() -> None:
    """An unknown sign name raises ValueError naming the bad value."""
    with pytest.raises(ValueError, match="Unknown sign 'Ophiuchus'"):
        sign_index("Ophiuchus")


@pytest.mark.parametrize(("degree", "tenths"), [(0.0, 0), (12.3, 123), (29.9, 299)])
def test_degree_to_tenths(degree: float, tenths: int) -> None:
    """Degrees convert to integer tenths without floating-point drift."""
    assert degree_to_tenths(degree) == tenths


@pytest.mark.parametrize(
    ("longitude", "sign", "degree"),
    [
        (0, "Aries", 0.0),
        (299, "Aries", 29.9),
        (300, "Taurus", 0.0),
        (1234, "Leo", 3.4),
        (3599, "Pisces", 29.9),
        (3600, "Aries", 0.0),
    ],
)
def test_sign_and_degree_at_boundaries(longitude: int, sign: str, degree: float) -> None:
    """Longitudes at sign edges map to the right sign and in-sign degree."""
    assert sign_of(longitude) == sign
    assert degree_in_sign(longitude) == degree


@pytest.mark.parametrize(
    ("longitude", "nakshatra"),
    [
        (0, "Ashvini"),
        (133, "Ashvini"),  # 13.3 degrees, just before 13 deg 20 min
        (134, "Bharani"),  # 13.4 degrees, just after
        (400, "Rohini"),  # exactly 40.0 degrees
        (3466, "Uttara Bhadrapada"),  # 346.6 degrees, last tenth before Revati
        (3467, "Revati"),  # 346.7 degrees, first tenth inside Revati (starts 346 deg 40 min)
        (3599, "Revati"),
    ],
)
def test_nakshatra_boundaries(longitude: int, nakshatra: str) -> None:
    """Nakshatras change exactly every 13 degrees 20 minutes."""
    assert nakshatra_of(longitude) == nakshatra


def test_every_nakshatra_is_reachable_at_one_decimal_resolution() -> None:
    """Sweeping every tenth of a degree visits all 27 nakshatras in order."""
    seen = [nakshatra_of(t) for t in range(3600)]
    deduplicated = [n for i, n in enumerate(seen) if i == 0 or seen[i - 1] != n]
    assert deduplicated == list(NAKSHATRAS)


def test_longitude_from_sign_degree_round_trips() -> None:
    """Splitting a longitude into sign and degree and rebuilding it gives the same value."""
    for longitude in range(0, 3600, 7):
        assert (
            longitude_from_sign_degree(sign_of(longitude), degree_in_sign(longitude)) == longitude
        )


@pytest.mark.parametrize("degree", [-0.1, 30.0, 45.0])
def test_longitude_from_sign_degree_rejects_out_of_range_degree(degree: float) -> None:
    """Degrees outside [0, 30) raise ValueError."""
    with pytest.raises(ValueError, match="degree must be in"):
        longitude_from_sign_degree("Aries", degree)


@pytest.mark.parametrize(
    ("sign", "ascendant", "house"),
    [
        ("Aries", "Aries", 1),
        ("Leo", "Aries", 5),
        ("Pisces", "Aries", 12),
        ("Aries", "Pisces", 2),
        ("Capricorn", "Cancer", 7),
    ],
)
def test_house_of_sign_counts_from_ascendant(sign: str, ascendant: str, house: int) -> None:
    """Houses are counted from the ascendant, which is always house 1."""
    assert house_of_sign(sign, ascendant) == house


@pytest.mark.parametrize("ascendant", SIGNS)
def test_house_and_sign_are_inverse(ascendant: str) -> None:
    """For any ascendant, sign_of_house and house_of_sign undo each other."""
    for house in range(1, 13):
        assert house_of_sign(sign_of_house(house, ascendant), ascendant) == house


@pytest.mark.parametrize("house", [0, 13, -1])
def test_sign_of_house_rejects_invalid_house(house: int) -> None:
    """House numbers outside 1-12 raise ValueError."""
    with pytest.raises(ValueError, match="house must be in"):
        sign_of_house(house, "Aries")


@pytest.mark.parametrize(
    ("longitude", "expected"), [(0, 1800), (100, 1900), (1800, 0), (3599, 1799)]
)
def test_opposite_is_180_degrees_away(longitude: int, expected: int) -> None:
    """The opposite point is exactly 180.0 degrees away, wrapping round."""
    assert opposite(longitude) == expected
    assert opposite(opposite(longitude)) == longitude


@pytest.mark.parametrize(
    ("first", "second", "distance"),
    [(0, 0, 0), (10, 3590, 20), (3590, 10, 20), (0, 1800, 1800), (100, 2000, 1700)],
)
def test_angular_distance_takes_shortest_path(first: int, second: int, distance: int) -> None:
    """The distance between two points is the shorter arc, at most 180 degrees."""
    assert angular_distance(first, second) == distance


@pytest.mark.parametrize("sign", SIGNS)
def test_nakshatra_segments_tile_each_sign(sign: str) -> None:
    """Each sign's nakshatra segments are contiguous and cover exactly 0 to 30 degrees."""
    segments = nakshatras_in_sign(sign)
    assert 2 <= len(segments) <= 3
    assert segments[0].start_degree == 0.0
    assert segments[-1].end_degree == pytest.approx(30.0)
    for before, after in pairwise(segments):
        assert before.end_degree == pytest.approx(after.start_degree)


def test_sign_nakshatra_map_covers_all_nakshatras() -> None:
    """Across all signs, the map lists every nakshatra, each in one or two signs."""
    names = [seg.nakshatra for segs in SIGN_NAKSHATRA_MAP.values() for seg in segs]
    assert set(names) == set(NAKSHATRAS)
    assert all(1 <= names.count(n) <= 2 for n in NAKSHATRAS)


@pytest.mark.parametrize("longitude", range(0, 3600, 13))
def test_sign_nakshatra_map_agrees_with_nakshatra_of(longitude: int) -> None:
    """The map and nakshatra_of give the same nakshatra for the same position."""
    sign, degree = sign_of(longitude), degree_in_sign(longitude)
    matching = [
        seg.nakshatra
        for seg in SIGN_NAKSHATRA_MAP[sign]
        if seg.start_degree <= degree < seg.end_degree
    ]
    assert matching == [nakshatra_of(longitude)]
