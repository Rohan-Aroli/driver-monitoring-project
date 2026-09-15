                         CAMERA
                            │
                            ▼
                   FACE DETECTION
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
             EAR           MAR        HEAD POSE
              │             │             │
              ▼             ▼             ▼
        DROWSINESS        YAWN        ATTENTION
         DETECTOR        DETECTOR      DETECTOR
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                  DRIVER STATE CLASSIFIER
                            │
                            ▼
                   REAL-TIME DATABASE
                            │
          ┌─────────────────┼──────────────────┐
          ▼                 ▼                  ▼
   driver_metrics    vehicle_metrics    emergency_events
          │                 │                  │
          └─────────────────┼──────────────────┘
                            │
                        TRIP ENDS
                            │
                            ▼
                 ┌─────────────────────┐
                 │ TripFeatureExtractor│
                 └──────────┬──────────┘
                            ▼
                     trip_features
                            │
                            ▼
                 ┌─────────────────────┐
                 │HistoricalFeatureEngine│
                 └──────────┬──────────┘
                            ▼
                  historical_features
                            │
                            ▼
                 ┌─────────────────────┐
                 │  ScoreNormalizer    │
                 └──────────┬──────────┘
                            ▼
                  normalized features
                            │
                            ▼
                 ┌─────────────────────┐
                 │   ComponentScorer   │
                 └──────────┬──────────┘
                            │
                    ┌───────┼───────┐
                    ▼       ▼       ▼
                    F       S       A
                    │       │       │
                    └───────┼───────┘
                            │
                         + E + H
                            │
                            ▼
                 ┌─────────────────────┐
                 │  DriverScoreEngine  │
                 └──────────┬──────────┘
                            ▼
                     RAW DRIVER SCORE
                            │
                            ▼
                  CRITICAL EVENT RULE
                            │
                            ▼
                    FINAL DRIVER SCORE
                            │
                            ▼
                 driver_score_history