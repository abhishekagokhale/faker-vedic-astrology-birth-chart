"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

import random

import pytest
from faker import Faker

from faker_vedic_astrology_birth_chart.chart import BirthChart, generate_birth_chart
from tests.support import VedicFaker, make_vedic_faker

#: Seed used wherever a test needs reproducible randomness.
SEED = 20261122


@pytest.fixture
def rng() -> random.Random:
    """Provide a seeded random number generator.

    Returns
    -------
    random.Random
        A fresh generator seeded with :data:`SEED`.
    """
    return random.Random(SEED)


@pytest.fixture
def fake() -> VedicFaker:
    """Provide a seeded Faker instance with the Vedic provider registered.

    Returns
    -------
    VedicFaker
        Faker instance ready to call ``vedic_*`` methods.
    """
    instance = make_vedic_faker()
    Faker.seed(SEED)
    return instance


@pytest.fixture(scope="session")
def many_charts() -> list[BirthChart]:
    """Provide a large, reproducible sample of generated charts.

    Shared across the session so statistical tests stay fast.

    Returns
    -------
    list of BirthChart
        20,000 charts generated from a seeded generator.
    """
    generator = random.Random(SEED)
    return [generate_birth_chart(generator) for _ in range(20_000)]
