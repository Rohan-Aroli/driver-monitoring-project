from typing import Optional


def clamp(value: float, minimum: float = 0.0,
          maximum: float = 100.0) -> float:

    return max(minimum, min(maximum, value))


def lower_is_better(
    value: Optional[float],
    low: float,
    high: float
) -> Optional[float]:

    if value is None:
        return None

    if high <= low:
        raise ValueError("high must be greater than low")

    if value <= low:
        return 100.0

    if value >= high:
        return 0.0

    score = 100.0 * (
        (high - value) / (high - low)
    )

    return clamp(score)


def higher_is_better(
    value: Optional[float],
    low: float,
    high: float
) -> Optional[float]:

    if value is None:
        return None

    if high <= low:
        raise ValueError("high must be greater than low")

    if value <= low:
        return 0.0

    if value >= high:
        return 100.0

    score = 100.0 * (
        (value - low) / (high - low)
    )

    return clamp(score)


def deviation_score(
    deviation: Optional[float],
    acceptable: float,
    severe: float
) -> Optional[float]:

    return lower_is_better(
        deviation,
        acceptable,
        severe
    )