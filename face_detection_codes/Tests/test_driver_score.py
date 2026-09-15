import pytest

from DriverScore.driver_score import DriverScoreEngine
from DriverScore.models import HistoricalFeatures


def history(hours=10):
    return HistoricalFeatures(
        driver_id="driver-1",
        trips_analyzed=3,
        driving_hours_analyzed=hours,
        avg_perclos=0.10,
        high_perclos_time_pct=5.0,
        drowsy_time_pct=5.0,
        drowsy_episode_rate=1.0,
        unresponsive_rate=0.0,
        unresponsive_time_pct=0.0,
        blink_deviation=0.1,
        yawn_rate=1.0,
        avg_yawn_duration=1.5,
        microsleep_rate=0.2,
        avg_microsleep_duration=2.5,
        max_microsleep_duration=3.0,
        distraction_rate=1.0,
        distracted_time_pct=2.0,
        emergency_rate=0.5,
        emergency_risk_rate=1.0,
        avg_speed=50.0,
        max_speed=70.0,
        avg_throttle=20.0,
        avg_brake=5.0,
        steering_variability=1.0,
    )


def test_raw_score_uses_weighted_components():
    engine = DriverScoreEngine()

    score = engine._calculate_raw_score(
        100,
        80,
        60,
        40,
        20,
    )

    expected = (
        100 * 0.35
        + 80 * 0.25
        + 60 * 0.15
        + 40 * 0.15
        + 20 * 0.10
    )

    assert score == pytest.approx(expected)


def test_missing_components_are_renormalized():
    engine = DriverScoreEngine()

    score = engine._calculate_raw_score(
        100,
        80,
        None,
        None,
        None,
    )

    expected = (
        100 * 0.35
        + 80 * 0.25
    ) / (0.35 + 0.25)

    assert score == pytest.approx(expected)


def test_no_valid_components_returns_none():
    assert DriverScoreEngine._calculate_raw_score(
        None,
        None,
        None,
        None,
        None,
    ) is None


def test_one_critical_event_caps_score_at_75():
    final, cap = DriverScoreEngine._apply_critical_constraints(
        90.0,
        1,
    )

    assert final == 75.0
    assert cap == 75.0


def test_repeated_critical_events_cap_score_at_50():
    final, cap = DriverScoreEngine._apply_critical_constraints(
        90.0,
        2,
    )

    assert final == 50.0
    assert cap == 50.0


def test_critical_event_does_not_raise_a_low_score():
    final, cap = DriverScoreEngine._apply_critical_constraints(
        40.0,
        1,
    )

    assert final == 40.0
    assert cap == 75.0


def test_confidence_bands():
    assert DriverScoreEngine._confidence(2) == "LOW"
    assert DriverScoreEngine._confidence(10) == "MEDIUM"
    assert DriverScoreEngine._confidence(30) == "HIGH"
    assert DriverScoreEngine._confidence(60) == "VERY_HIGH"


def test_full_driver_score_calculation():
    engine = DriverScoreEngine()

    result = engine.calculate(
        driver_id="driver-1",
        fatigue_score=90.0,
        safety_score=80.0,
        attention_score=70.0,
        experience_score=60.0,
        health_score=50.0,
        historical_features=history(10),
        critical_events=0,
        data_quality=0.95,
    )

    expected = (
        90 * 0.35
        + 80 * 0.25
        + 70 * 0.15
        + 60 * 0.15
        + 50 * 0.10
    )

    assert result.driver_id == "driver-1"
    assert result.raw_driver_score == pytest.approx(expected)
    assert result.final_driver_score == pytest.approx(expected)
    assert result.critical_event is False
    assert result.score_cap is None
    assert result.trips_analyzed == 3
    assert result.driving_hours_analyzed == 10
    assert result.score_confidence == "MEDIUM"
    assert result.data_quality == pytest.approx(0.95)
    assert result.normalization_version == "1.0"


def test_full_driver_score_applies_critical_cap():
    engine = DriverScoreEngine()

    result = engine.calculate(
        driver_id="driver-1",
        fatigue_score=100.0,
        safety_score=100.0,
        attention_score=100.0,
        experience_score=100.0,
        health_score=100.0,
        historical_features=history(30),
        critical_events=1,
    )

    assert result.raw_driver_score == pytest.approx(100.0)
    assert result.final_driver_score == pytest.approx(75.0)
    assert result.critical_event is True
    assert result.score_cap == 75.0
    assert result.score_confidence == "HIGH"