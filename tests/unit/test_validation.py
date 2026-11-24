"""Unit tests for chart validation in :mod:`faker_vedic_astrology_birth_chart.chart`.

Each test takes a known-good chart, breaks exactly one rule, and checks
that :func:`validate_birth_chart` rejects it with a clear message.
"""

from __future__ import annotations

import random
from typing import Any

import pytest

from faker_vedic_astrology_birth_chart.chart import (
    InvalidBirthChartError,
    generate_birth_chart,
    validate_birth_chart,
    validate_placement,
)
from faker_vedic_astrology_birth_chart.zodiac import (
    angular_distance,
    longitude_from_sign_degree,
    nakshatra_of,
)


def _good_chart() -> list[dict[str, Any]]:
    """Return a valid chart as a list of mutable dicts.

    Returns
    -------
    list of dict
        A copy of a seeded chart with ascendant Aries, which tests can edit.
    """
    chart = generate_birth_chart(random.Random(7), ascendant="Aries")
    return [dict(p) for p in chart]


def _index(chart: list[dict[str, Any]], planet: str) -> int:
    """Return the list position of a planet in a chart.

    Parameters
    ----------
    chart : list of dict
        The chart to search.
    planet : str
        Planet name.

    Returns
    -------
    int
        Index of the planet's placement.
    """
    return next(i for i, p in enumerate(chart) if p["planet"] == planet)


def test_valid_chart_passes_and_returns_ascendant() -> None:
    """A generated chart passes validation and reports its ascendant."""
    assert validate_birth_chart(tuple(_good_chart()), ascendant="Aries") == "Aries"


def test_chart_must_be_a_tuple() -> None:
    """A list is rejected because charts are defined as tuples."""
    with pytest.raises(InvalidBirthChartError, match="must be a tuple"):
        validate_birth_chart(_good_chart())


def test_chart_must_have_nine_placements() -> None:
    """A chart with a planet missing is rejected."""
    with pytest.raises(InvalidBirthChartError, match="9 placements"):
        validate_birth_chart(tuple(_good_chart()[:8]))


def test_planets_must_not_repeat() -> None:
    """A chart with the same planet twice is rejected."""
    chart = _good_chart()
    chart[_index(chart, "Moon")] = dict(chart[_index(chart, "Sun")])
    with pytest.raises(InvalidBirthChartError, match="exactly once"):
        validate_birth_chart(tuple(chart))


def test_placement_must_have_exactly_six_keys() -> None:
    """An extra key in a placement is rejected."""
    placement = {**_good_chart()[0], "pada": 1}
    with pytest.raises(InvalidBirthChartError, match="placement keys"):
        validate_placement(placement)


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("planet", "Pluto", "unknown planet"),
        ("house", 0, "house must be"),
        ("house", 13, "house must be"),
        ("house", True, "house must be"),
        ("house", 1.0, "house must be"),
        ("sign", "Ophiuchus", "unknown sign"),
        ("nakshatra", "Abhijit", "unknown nakshatra"),
        ("degree", 30.0, "degree must be"),
        ("degree", -0.1, "degree must be"),
        ("degree", 12.34, "degree must be"),
        ("degree", 12, "degree must be"),
        ("retrograde", "maybe", "retrograde must be"),
        ("retrograde", True, "retrograde must be"),
    ],
)
def test_placement_values_must_be_valid(key: str, value: object, message: str) -> None:
    """Out-of-range or wrongly typed values are rejected."""
    chart = _good_chart()
    chart[_index(chart, "Saturn")][key] = value
    with pytest.raises(InvalidBirthChartError, match=message):
        validate_birth_chart(tuple(chart))


@pytest.mark.parametrize("planet", ["Sun", "Moon"])
def test_luminaries_cannot_be_retrograde(planet: str) -> None:
    """Sun or Moon marked retrograde is rejected."""
    chart = _good_chart()
    chart[_index(chart, planet)]["retrograde"] = "yes"
    with pytest.raises(InvalidBirthChartError, match="never be retrograde"):
        validate_birth_chart(tuple(chart))


@pytest.mark.parametrize("planet", ["Rahu", "Ketu"])
def test_nodes_must_be_retrograde(planet: str) -> None:
    """Rahu or Ketu marked direct is rejected."""
    chart = _good_chart()
    chart[_index(chart, planet)]["retrograde"] = "no"
    with pytest.raises(InvalidBirthChartError, match="always retrograde"):
        validate_birth_chart(tuple(chart))


def test_nakshatra_must_match_sign_and_degree() -> None:
    """A nakshatra that does not contain the sign and degree is rejected."""
    chart = _good_chart()
    chart[0].update(sign="Aries", degree=1.0, nakshatra="Revati", house=1)
    with pytest.raises(InvalidBirthChartError, match="lies in Ashvini"):
        validate_birth_chart(tuple(chart))


def test_houses_must_agree_with_one_ascendant() -> None:
    """Moving one planet's house without changing its sign is rejected."""
    chart = _good_chart()
    moon = chart[_index(chart, "Moon")]
    moon["house"] = moon["house"] % 12 + 1
    with pytest.raises(InvalidBirthChartError, match="single ascendant"):
        validate_birth_chart(tuple(chart))


def test_expected_ascendant_is_checked() -> None:
    """Asking for a different ascendant from the chart's own is rejected."""
    with pytest.raises(InvalidBirthChartError, match="expected Leo"):
        validate_birth_chart(tuple(_good_chart()), ascendant="Leo")


def test_rahu_and_ketu_must_be_opposite() -> None:
    """Moving Ketu by a tenth of a degree breaks the 180-degree rule."""
    chart = _good_chart()
    ketu = chart[_index(chart, "Ketu")]
    degree = ketu["degree"]
    shifted = round(degree + 0.1, 1) if degree < 29.9 else round(degree - 0.1, 1)
    # Keep the nakshatra consistent so only the opposition rule fails.
    ketu.update(
        degree=shifted,
        nakshatra=nakshatra_of(longitude_from_sign_degree(ketu["sign"], shifted)),
    )
    with pytest.raises(InvalidBirthChartError, match="180 degrees apart"):
        validate_birth_chart(tuple(chart))


def test_inner_planet_check_is_optional() -> None:
    """A chart with Mercury far from the Sun passes unless the check is requested."""
    rng = random.Random(3)
    chart = next(
        c
        for c in (generate_birth_chart(rng, constrain_inner_planets=False) for _ in range(500))
        if _mercury_far_from_sun(c)
    )
    validate_birth_chart(chart)
    with pytest.raises(InvalidBirthChartError, match="Mercury must be within 28"):
        validate_birth_chart(chart, constrain_inner_planets=True)


def _mercury_far_from_sun(chart: tuple[Any, ...]) -> bool:
    """Return whether Mercury is more than 28 degrees from the Sun.

    Parameters
    ----------
    chart : tuple of dict
        A generated chart.

    Returns
    -------
    bool
        ``True`` if Mercury is outside its real elongation limit.
    """
    lon = {p["planet"]: longitude_from_sign_degree(p["sign"], p["degree"]) for p in chart}
    return angular_distance(lon["Mercury"], lon["Sun"]) > 280
