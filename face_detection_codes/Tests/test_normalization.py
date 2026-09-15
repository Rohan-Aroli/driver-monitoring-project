import pytest

from DriverScore.normalization import (
    clamp,
    lower_is_better,
    higher_is_better,
    deviation_score,
)


def test_clamp_limits_values():
    assert clamp(-10) == 0.0
    assert clamp(50) == 50
    assert clamp(120) == 100.0


def test_lower_is_better_boundaries():
    assert lower_is_better(0, 0, 10) == 100.0
    assert lower_is_better(10, 0, 10) == 0.0
    assert lower_is_better(5, 0, 10) == 50.0


def test_lower_is_better_outside_range():
    assert lower_is_better(-5, 0, 10) == 100.0
    assert lower_is_better(15, 0, 10) == 0.0


def test_higher_is_better_boundaries():
    assert higher_is_better(0, 0, 10) == 0.0
    assert higher_is_better(10, 0, 10) == 100.0
    assert higher_is_better(5, 0, 10) == 50.0


def test_higher_is_better_outside_range():
    assert higher_is_better(-5, 0, 10) == 0.0
    assert higher_is_better(15, 0, 10) == 100.0


def test_none_is_preserved():
    assert lower_is_better(None, 0, 10) is None
    assert higher_is_better(None, 0, 10) is None
    assert deviation_score(None, 0, 1) is None


def test_invalid_normalization_range_raises():
    with pytest.raises(ValueError):
        lower_is_better(5, 10, 10)

    with pytest.raises(ValueError):
        higher_is_better(5, 10, 0)