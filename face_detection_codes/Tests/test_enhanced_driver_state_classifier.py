from unittest.mock import patch

from core.enhanced_driver_state_classifier import (
    EnhancedDriverStateClassifier,
)


def test_calibrated_classifier_recovers_after_healthy_interval():
    classifier = EnhancedDriverStateClassifier(
        {
            "ear_mean": 0.30,
            "perclos_mean": 0.10,
            "perclos_std": 0.02,
            "pitch_mean": 0.0,
            "yaw_mean": 0.0,
            "roll_mean": 0.0,
        },
        recovery_time=2,
    )

    normal = {
        "face_detected": True,
        "eyes_detected": True,
        "ear": 0.30,
        "perclos": 0.10,
        "drowsiness_score": 0.1,
        "continuous_eye_closure": 0,
        "microsleep_detected": False,
        "pitch": 0,
        "yaw": 0,
        "roll": 0,
        "is_yawning": False,
        "yawn_count": 0,
    }
    drowsy = dict(
        normal,
        ear=0.18,
        perclos=0.40,
        drowsiness_score=0.7,
        continuous_eye_closure=2.5,
        microsleep_detected=True,
    )

    with patch(
        "core.enhanced_driver_state_classifier.time.time",
        side_effect=[100, 101, 102, 104],
    ):
        assert classifier.classify(normal) == "NORMAL"
        assert classifier.classify(drowsy) == "DROWSY"
        assert classifier.classify(normal) == "DROWSY"
        assert classifier.classify(normal) == "NORMAL"


def test_head_pose_is_compared_with_calibrated_neutral_pose():
    classifier = EnhancedDriverStateClassifier(
        {"pitch_mean": 176.0, "yaw_mean": 0.0, "roll_mean": 0.0}
    )

    metrics = {
        "face_detected": True,
        "eyes_detected": True,
        "ear": 0.30,
        "perclos": 0.0,
        "drowsiness_score": 0.0,
        "continuous_eye_closure": 0,
        "microsleep_detected": False,
        "pitch": 176.0,
        "yaw": 0.0,
        "roll": 0.0,
        "is_yawning": False,
        "yawn_count": 0,
    }

    assert classifier.classify(metrics) == "NORMAL"