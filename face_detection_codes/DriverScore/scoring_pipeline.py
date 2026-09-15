from .trip_features import TripFeatureExtractor
from .historical_features import HistoricalFeatureEngine
from .component_scores import ComponentScorer
from .driver_score import DriverScoreEngine


class ScoringPipeline:

    def __init__(
        self,
        repository,
        perclos_threshold=0.20,
        recency_lambda=0.01
    ):

        self.repository = repository

        self.trip_extractor = (
            TripFeatureExtractor(
                perclos_high_threshold=
                    perclos_threshold
            )
        )

        self.history_engine = (
            HistoricalFeatureEngine(
                recency_lambda=
                    recency_lambda
            )
        )

        self.component_scorer = (
            ComponentScorer()
        )

        self.score_engine = (
            DriverScoreEngine()
        )

    # ======================================
    # Main entry point
    # ======================================

    def process_trip(
        self,
        trip_context
    ):

        # -------------------------------
        # 1. Fetch raw data
        # -------------------------------

        driver_metrics = (
            self.repository
            .get_trip_driver_metrics(
                trip_context.trip_id
            )
        )

        vehicle_metrics = (
            self.repository
            .get_trip_vehicle_metrics(
                trip_context.trip_id
            )
        )

        emergency_events = (
            self.repository
            .get_trip_emergency_events(
                trip_context.trip_id
            )
        )

        # -------------------------------
        # 2. Fetch baseline
        # -------------------------------

        baseline = (
            self.repository
            .get_driver_baseline(
                trip_context.driver_id
            )
        )

        # -------------------------------
        # 3. Extract current trip
        # -------------------------------

        trip_features = (
            self.trip_extractor.extract(
                context=trip_context,
                driver_metrics=driver_metrics,
                vehicle_metrics=vehicle_metrics,
                emergency_events=emergency_events,
                baseline=baseline
            )
        )

        # -------------------------------
        # 4. Save trip features
        # -------------------------------

        self.repository.save_trip_features(
            trip_features
        )

        # -------------------------------
        # 5. Fetch historical trips
        # -------------------------------

        previous_trips = (
            self.repository
            .get_previous_trip_features(
                trip_context.driver_id
            )
        )

        all_trips = (
            previous_trips +
            [trip_features]
        )

        # -------------------------------
        # 6. Historical aggregation
        # -------------------------------

        historical = (
            self.history_engine.aggregate(
                trips=all_trips,
                reference_time=
                    trip_context.trip_end
            )
        )

        # -------------------------------
        # 7. Normalize
        # -------------------------------

        normalized = (
            self.component_scorer.normalize(
                historical
            )
        )

        # -------------------------------
        # 8. Components
        # -------------------------------

        fatigue = (
            self.component_scorer
            .fatigue_score(
                normalized
            )
        )

        attention = (
            self.component_scorer
            .attention_score(
                normalized
            )
        )

        safety = (
            self.component_scorer
            .safety_score(
                normalized
            )
        )

        # -------------------------------
        # 9. Profile scores
        # -------------------------------

        profile = (
            self.repository
            .get_driver_profile(
                trip_context.driver_id
            )
        )

        experience = profile.get(
            "experience_score"
        )

        health = profile.get(
            "health_score"
        )

        # -------------------------------
        # 10. Critical events
        # -------------------------------

        critical_events = (
            self.repository
            .count_recent_critical_events(
                trip_context.driver_id
            )
        )

        # -------------------------------
        # 11. Final score
        # -------------------------------

        score = self.score_engine.calculate(
            driver_id=
                trip_context.driver_id,

            fatigue_score=fatigue,
            safety_score=safety,
            attention_score=attention,

            experience_score=experience,
            health_score=health,

            historical_features=historical,

            critical_events=critical_events,

            data_quality=self._data_quality(
                trip_features
            )
        )

        # -------------------------------
        # 12. Save score
        # -------------------------------

        self.repository.save_score_history(
            score,
            trip_context.trip_id
        )

        return score

    @staticmethod
    def _data_quality(
        trip_features
    ):

        return (
            trip_features.driver_data_coverage +
            trip_features.vehicle_data_coverage
        ) / 2.0