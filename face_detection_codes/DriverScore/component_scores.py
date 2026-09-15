from .models import (
    HistoricalFeatures,
    NormalizedFeatures
)

from .normalization import (
    lower_is_better,
    deviation_score
)

from .config import (
    FATIGUE_WEIGHTS,
    MICROSLEEP_WEIGHTS,
    YAWN_WEIGHTS,
    ATTENTION_WEIGHTS,
    SAFETY_WEIGHTS,
    PERCLOS_LOW,
    PERCLOS_HIGH
)


class ComponentScorer:

    # ======================================
    # Normalization
    # ======================================

    @staticmethod
    def normalize(
        features: HistoricalFeatures
    ) -> NormalizedFeatures:
        
# PROVISIONAL ENGINEERING VALUES.
# Replace after empirical calibration.
        # -----------------------------
        # PERCLOS
        # -----------------------------

        perclos_score = lower_is_better(
            features.avg_perclos,
            PERCLOS_LOW,
            PERCLOS_HIGH
        )

        high_perclos_score = lower_is_better(
            features.high_perclos_time_pct,
            0.0,
            30.0
        )

        # -----------------------------
        # Drowsiness
        # -----------------------------

        drowsy_time_score = lower_is_better(
            features.drowsy_time_pct,
            0.0,
            30.0
        )

        drowsy_episode_score = lower_is_better(
            features.drowsy_episode_rate,
            0.0,
            5.0
        )

        # -----------------------------
        # Unresponsive
        # -----------------------------

        unresponsive_score = lower_is_better(
            features.unresponsive_rate,
            0.0,
            1.0
        )

        # -----------------------------
        # Blink
        # -----------------------------

        blink_score = deviation_score(
            features.blink_deviation,
            0.0,
            1.0
        )

        # -----------------------------
        # Yawning
        # -----------------------------

        yawn_rate_score = lower_is_better(
            features.yawn_rate,
            0.0,
            5.0
        )

        yawn_duration_score = lower_is_better(
            features.avg_yawn_duration,
            1.0,
            5.0
        )

        # -----------------------------
        # Microsleep
        # -----------------------------

        microsleep_rate_score = lower_is_better(
            features.microsleep_rate,
            0.0,
            2.0
        )

        microsleep_duration_score = lower_is_better(
            features.avg_microsleep_duration,
            2.0,
            6.0
        )

        max_microsleep_score = lower_is_better(
            features.max_microsleep_duration,
            2.0,
            10.0
        )

        # -----------------------------
        # Attention
        # -----------------------------

        distraction_rate_score = lower_is_better(
            features.distraction_rate,
            0.0,
            5.0
        )

        distracted_time_score = lower_is_better(
            features.distracted_time_pct,
            0.0,
            10.0
        )

        # -----------------------------
        # Safety
        # -----------------------------

        emergency_score = lower_is_better(
            features.emergency_risk_rate,
            0.0,
            5.0
        )

        # These remain placeholders until
        # vehicle telemetry units are verified.

        braking_score = None
        acceleration_score = None
        steering_score = None

        return NormalizedFeatures(

            perclos_score=perclos_score,
            high_perclos_score=high_perclos_score,

            drowsy_time_score=drowsy_time_score,
            drowsy_episode_score=drowsy_episode_score,

            unresponsive_score=unresponsive_score,

            blink_score=blink_score,

            yawn_rate_score=yawn_rate_score,
            yawn_duration_score=yawn_duration_score,

            microsleep_rate_score=
                microsleep_rate_score,

            microsleep_duration_score=
                microsleep_duration_score,

            max_microsleep_score=
                max_microsleep_score,

            distraction_rate_score=
                distraction_rate_score,

            distracted_time_score=
                distracted_time_score,

            emergency_score=emergency_score,

            braking_score=braking_score,
            acceleration_score=acceleration_score,
            steering_score=steering_score
        )

    # ======================================
    # Fatigue
    # ======================================

    @staticmethod
    def fatigue_score(
        normalized: NormalizedFeatures
    ):

        values = []

        # P
        if normalized.perclos_score is not None:
            values.append((
                normalized.perclos_score,
                FATIGUE_WEIGHTS["perclos"]
            ))

        # M
        microsleep_parts = []

        if normalized.microsleep_rate_score is not None:
            microsleep_parts.append((
                normalized.microsleep_rate_score,
                MICROSLEEP_WEIGHTS["rate"]
            ))

        if normalized.microsleep_duration_score is not None:
            microsleep_parts.append((
                normalized.microsleep_duration_score,
                MICROSLEEP_WEIGHTS[
                    "average_duration"
                ]
            ))

        if normalized.max_microsleep_score is not None:
            microsleep_parts.append((
                normalized.max_microsleep_score,
                MICROSLEEP_WEIGHTS[
                    "maximum_duration"
                ]
            ))

        M = ComponentScorer._weighted(
            microsleep_parts
        )

        if M is not None:
            values.append((
                M,
                FATIGUE_WEIGHTS["microsleep"]
            ))

        # Y
        yawn_parts = []

        if normalized.yawn_rate_score is not None:
            yawn_parts.append((
                normalized.yawn_rate_score,
                YAWN_WEIGHTS["rate"]
            ))

        if normalized.yawn_duration_score is not None:
            yawn_parts.append((
                normalized.yawn_duration_score,
                YAWN_WEIGHTS["duration"]
            ))

        Y = ComponentScorer._weighted(
            yawn_parts
        )

        if Y is not None:
            values.append((
                Y,
                FATIGUE_WEIGHTS["yawn"]
            ))

        # D
        D = ComponentScorer._weighted([
            (
                normalized.drowsy_time_score,
                0.70
            ),
            (
                normalized.drowsy_episode_score,
                0.30
            )
        ])

        if D is not None:
            values.append((
                D,
                FATIGUE_WEIGHTS["drowsiness"]
            ))

        # U
        if normalized.unresponsive_score is not None:
            values.append((
                normalized.unresponsive_score,
                FATIGUE_WEIGHTS[
                    "unresponsive"
                ]
            ))

        return ComponentScorer._renormalized(
            values
        )

    # ======================================
    # Attention
    # ======================================

    @staticmethod
    def attention_score(
        normalized: NormalizedFeatures
    ):

        values = [
            (
                normalized.distraction_rate_score,
                ATTENTION_WEIGHTS[
                    "distraction_rate"
                ]
            ),
            (
                normalized.distracted_time_score,
                ATTENTION_WEIGHTS[
                    "distracted_time"
                ]
            ),
            (
                normalized.blink_score,
                ATTENTION_WEIGHTS["blink"]
            )
        ]

        return ComponentScorer._renormalized(
            values
        )

    # ======================================
    # Safety
    # ======================================

    @staticmethod
    def safety_score(
        normalized: NormalizedFeatures
    ):

        values = [
            (
                normalized.emergency_score,
                SAFETY_WEIGHTS[
                    "emergency"
                ]
            ),
            (
                normalized.braking_score,
                SAFETY_WEIGHTS[
                    "braking"
                ]
            ),
            (
                normalized.acceleration_score,
                SAFETY_WEIGHTS[
                    "acceleration"
                ]
            ),
            (
                normalized.steering_score,
                SAFETY_WEIGHTS[
                    "steering"
                ]
            )
        ]

        return ComponentScorer._renormalized(
            values
        )

    # ======================================
    # Helpers
    # ======================================

    @staticmethod
    def _weighted(values):

        valid = [
            (value, weight)
            for value, weight in values
            if value is not None
        ]

        if not valid:
            return None

        total_weight = sum(
            weight
            for _, weight in valid
        )

        if total_weight <= 0:
            return None

        return sum(
            value * weight
            for value, weight in valid
        ) / total_weight

    @staticmethod
    def _renormalized(values):

        return ComponentScorer._weighted(
            values
        )