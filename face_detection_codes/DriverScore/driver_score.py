from .models import DriverScore
from .config import (
    DRIVER_SCORE_WEIGHTS,
    ONE_UNRESPONSIVE_SCORE_CAP,
    REPEATED_CRITICAL_SCORE_CAP,
    NORMALIZATION_VERSION,
    LOW_CONFIDENCE_HOURS,
    MEDIUM_CONFIDENCE_HOURS,
    HIGH_CONFIDENCE_HOURS,
)


class DriverScoreEngine:

    def calculate(
        self,
        driver_id,
        fatigue_score,
        safety_score,
        attention_score,
        experience_score,
        health_score,
        historical_features,
        critical_events=0,
        data_quality=0.0
    ):

        raw_score = self._calculate_raw_score(
            fatigue_score,
            safety_score,
            attention_score,
            experience_score,
            health_score
        )

        final_score, cap = (
            self._apply_critical_constraints(
                raw_score,
                critical_events
            )
        )

        confidence = self._confidence(
            historical_features.driving_hours_analyzed
        )

        return DriverScore(
            driver_id=driver_id,

            fatigue_score=fatigue_score,
            safety_score=safety_score,
            attention_score=attention_score,

            experience_score=experience_score,
            health_score=health_score,

            raw_driver_score=raw_score,
            final_driver_score=final_score,

            critical_event=(
                critical_events > 0
            ),

            score_cap=cap,

            trips_analyzed=
                historical_features.trips_analyzed,

            driving_hours_analyzed=
                historical_features.driving_hours_analyzed,

            score_confidence=confidence,

            data_quality=data_quality,

            normalization_version=
                NORMALIZATION_VERSION
        )

    # ======================================
    # Raw score
    # ======================================

    @staticmethod
    def _calculate_raw_score(
        fatigue,
        safety,
        attention,
        experience,
        health
    ):

        components = [
            (fatigue,
             DRIVER_SCORE_WEIGHTS["fatigue"]),

            (safety,
             DRIVER_SCORE_WEIGHTS["safety"]),

            (attention,
             DRIVER_SCORE_WEIGHTS["attention"]),

            (experience,
             DRIVER_SCORE_WEIGHTS["experience"]),

            (health,
             DRIVER_SCORE_WEIGHTS["health"]),
        ]

        valid = [
            (score, weight)
            for score, weight in components
            if score is not None
        ]

        if not valid:
            return None

        total_weight = sum(
            weight
            for _, weight in valid
        )

        weighted_sum = sum(
            score * weight
            for score, weight in valid
        )

        # Renormalize if some profile
        # components are unavailable.
        return weighted_sum / total_weight

    # ======================================
    # Critical events
    # ======================================

    @staticmethod
    def _apply_critical_constraints(
        raw_score,
        critical_events
    ):

        if raw_score is None:
            return None, None

        if critical_events >= 2:

            return (
                min(
                    raw_score,
                    REPEATED_CRITICAL_SCORE_CAP
                ),
                REPEATED_CRITICAL_SCORE_CAP
            )

        if critical_events == 1:

            return (
                min(
                    raw_score,
                    ONE_UNRESPONSIVE_SCORE_CAP
                ),
                ONE_UNRESPONSIVE_SCORE_CAP
            )

        return raw_score, None

    # ======================================
    # Confidence
    # ======================================

    @staticmethod
    def _confidence(hours):

        if hours < LOW_CONFIDENCE_HOURS:
            return "LOW"

        if hours < MEDIUM_CONFIDENCE_HOURS:
            return "MEDIUM"

        if hours < HIGH_CONFIDENCE_HOURS:
            return "HIGH"

        return "VERY_HIGH"