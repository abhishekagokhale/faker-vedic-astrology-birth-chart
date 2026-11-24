"""Integration tests: the provider registered with a real :class:`faker.Faker`.

These tests check that every public ``vedic_*`` method is available on a
Faker instance, returns valid data, and is reproducible with
``Faker.seed``.
"""

from __future__ import annotations

import pytest
from faker import Faker

from faker_vedic_astrology_birth_chart import (
    NAKSHATRAS,
    PLANETS,
    SIGNS,
    Provider,
    VedicAstrologyProvider,
    validate_birth_chart,
)
from faker_vedic_astrology_birth_chart.chart import PLACEMENT_KEYS, validate_placement
from tests.support import VedicFaker, make_vedic_faker


def test_provider_alias_is_the_same_class() -> None:
    """``Provider`` is an alias for ``VedicAstrologyProvider``."""
    assert Provider is VedicAstrologyProvider


def test_methods_are_registered_on_faker(fake: VedicFaker) -> None:
    """All public provider methods can be called on the Faker instance."""
    for name in (
        "vedic_planet",
        "vedic_sign",
        "vedic_nakshatra",
        "vedic_degree",
        "vedic_ascendant",
        "vedic_retrograde",
        "vedic_planet_placement",
        "vedic_birth_chart",
    ):
        assert callable(getattr(fake, name))


def test_simple_value_methods_return_known_values(fake: VedicFaker) -> None:
    """Planet, sign, nakshatra and ascendant methods return values from the reference lists."""
    for _ in range(200):
        assert fake.vedic_planet() in PLANETS
        assert fake.vedic_sign() in SIGNS
        assert fake.vedic_nakshatra() in NAKSHATRAS
        assert fake.vedic_ascendant() in SIGNS


def test_vedic_degree_is_one_decimal_in_range(fake: VedicFaker) -> None:
    """Degrees are floats in [0.0, 30.0) with one decimal place."""
    for _ in range(1_000):
        degree = fake.vedic_degree()
        assert isinstance(degree, float)
        assert 0.0 <= degree < 30.0
        assert round(degree, 1) == degree


def test_vedic_retrograde_follows_fixed_rules(fake: VedicFaker) -> None:
    """Sun/Moon are never retrograde and Rahu/Ketu always are."""
    for _ in range(100):
        assert fake.vedic_retrograde("Sun") == "no"
        assert fake.vedic_retrograde("Moon") == "no"
        assert fake.vedic_retrograde("Rahu") == "yes"
        assert fake.vedic_retrograde("Ketu") == "yes"


def test_vedic_retrograde_rejects_unknown_planet(fake: VedicFaker) -> None:
    """An unknown planet raises ValueError rather than KeyError."""
    with pytest.raises(ValueError, match="Unknown planet"):
        fake.vedic_retrograde("Pluto")


def test_vedic_planet_placement_is_valid(fake: VedicFaker) -> None:
    """Single placements pass validation and honour requested planet and ascendant."""
    for _ in range(300):
        validate_placement(fake.vedic_planet_placement())
    placement = fake.vedic_planet_placement(planet="Saturn", ascendant="Libra")
    assert placement["planet"] == "Saturn"
    assert tuple(placement) == PLACEMENT_KEYS
    assert (placement["house"] == 1) == (placement["sign"] == "Libra")


def test_vedic_planet_placement_rejects_bad_input(fake: VedicFaker) -> None:
    """Unknown planet or ascendant names raise ValueError."""
    with pytest.raises(ValueError, match="Unknown planet"):
        fake.vedic_planet_placement(planet="Pluto")
    with pytest.raises(ValueError, match="Unknown sign"):
        fake.vedic_planet_placement(ascendant="Ophiuchus")


def test_vedic_birth_chart_is_always_valid(fake: VedicFaker) -> None:
    """Every generated chart passes all rules, including the inner-planet check."""
    for _ in range(1_000):
        validate_birth_chart(fake.vedic_birth_chart(), constrain_inner_planets=True)


def test_vedic_birth_chart_has_54_values(fake: VedicFaker) -> None:
    """A chart holds 9 placements x 6 keys = 54 values."""
    chart = fake.vedic_birth_chart()
    assert sum(len(p) for p in chart) == 54


def test_vedic_birth_chart_uses_requested_ascendant(fake: VedicFaker) -> None:
    """Passing an ascendant from vedic_ascendant fixes house 1 to that sign."""
    ascendant = fake.vedic_ascendant()
    chart = fake.vedic_birth_chart(ascendant=ascendant)
    assert validate_birth_chart(chart, ascendant=ascendant) == ascendant


def test_vedic_birth_chart_rejects_unknown_ascendant(fake: VedicFaker) -> None:
    """An unknown ascendant raises ValueError."""
    with pytest.raises(ValueError, match="Unknown sign"):
        fake.vedic_birth_chart(ascendant="Ophiuchus")


def test_faker_seed_makes_charts_reproducible(fake: VedicFaker) -> None:
    """Re-seeding Faker with the same value gives the same charts."""
    Faker.seed(99)
    first = [fake.vedic_birth_chart() for _ in range(5)]
    Faker.seed(99)
    second = [fake.vedic_birth_chart() for _ in range(5)]
    assert first == second


def test_provider_works_alongside_other_locales() -> None:
    """The provider is locale-independent and works with a non-English Faker."""
    fake = make_vedic_faker("hi_IN")
    validate_birth_chart(fake.vedic_birth_chart())


def test_seeded_output_matches_readme_example(fake: VedicFaker) -> None:
    """``Faker.seed(42)`` reproduces the exact chart shown in the README.

    This pins the generation order: if it changes, seeded output for users
    changes too, so the README and CHANGELOG must be updated.
    """
    Faker.seed(42)
    chart = fake.vedic_birth_chart()
    summary = [(p["planet"], p["house"], p["sign"], p["degree"]) for p in chart]
    assert summary[0] == ("Sun", 4, "Taurus", 15.6)
    assert summary[2] == ("Mars", 1, "Aquarius", 3.7)
    assert summary[-1] == ("Ketu", 7, "Leo", 1.6)
