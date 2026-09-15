driver-monitoring-project/
│
├── face_detection_codes/
│   ├── main.py
│   ├── drowsiness_detector.py
│   ├── yawn_detector.py
│   ├── microsleep_detector.py
│   ├── head_pose_estimator.py
│   ├── enhanced_driver_state_classifier.py
│   ├── push_metrics.py
│   └── ...
│
├── driver_scoring/
│   ├── __init__.py
│   │
│   ├── models.py
│   ├── config.py
│   ├── db_repository.py
│   │
│   ├── trip_features.py
│   ├── historical_features.py
│   ├── normalization.py
│   ├── component_scores.py
│   ├── driver_score.py
│   │
│   └── scoring_pipeline.py
│
├── tests/
│   ├── test_trip_features.py
│   ├── test_historical_features.py
│   ├── test_normalization.py
│   └── test_driver_score.py
│
├── baselines/
│
├── shared/
│
└── requirements.txt