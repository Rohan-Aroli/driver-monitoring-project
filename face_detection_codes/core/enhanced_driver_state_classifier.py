import time


class EnhancedDriverStateClassifier:

    def __init__(self, profile=None, missing_timeout=4, recovery_time=2):

        self.state = "NORMAL"
        self.profile = profile or {}

        self.missing_start_time = None
        self.missing_timeout = missing_timeout
        self.healthy_start_time = None
        self.recovery_time = recovery_time

    def update_profile(self, profile):
        self.profile = profile or {}

    @staticmethod
    def _number(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _thresholds(self):
        ear_mean = self._number(self.profile.get("ear_mean"), 0.30)
        perclos_mean = self._number(self.profile.get("perclos_mean"), 0.10)
        perclos_std = self._number(self.profile.get("perclos_std"), 0.0)
        blink_mean = self._number(self.profile.get("blink_rate_mean"), 15.0)
        closure_mean = self._number(
            self.profile.get(
                "eye_closure_duration_mean",
                self.profile.get("closure_mean"),
            ),
            0.0,
        )

        return {
            "ear_closed": max(0.16, min(0.30, ear_mean * 0.82)),
            "perclos_drowsy": max(0.25, perclos_mean + (2.0 * perclos_std)),
            "blink_low": max(1.0, blink_mean * 0.5),
            "closure_drowsy": max(1.5, closure_mean + 1.0),
        }

    def _angle_deviation(self, value, key):
        baseline = self._number(self.profile.get(key), 0.0)
        difference = (value - baseline + 180.0) % 360.0 - 180.0
        return abs(difference)

    def get_ear_threshold(self):
        return self._thresholds()["ear_closed"]

    # ---------------------------------------------------
    # MAIN CLASSIFIER
    # ---------------------------------------------------
    def classify(self, features):

        try:

            current_time = time.time()

            # ---------------------------------------
            # Fetch features
            # ---------------------------------------

            face_detected = features.get(
                "face_detected", True
            )

            eyes_detected = features.get(
                "eyes_detected", True
            )

            perclos = self._number(features.get("perclos"))

            ear = self._number(features.get("ear"))

            fatigue_score = self._number(
                features.get("drowsiness_score")
            )

            yawn_count = features.get(
                "yawn_count", 0
            )

            is_yawning = features.get(
                "is_yawning", False
            )

            closure_duration = self._number(
                features.get("continuous_eye_closure")
            )

            microsleep = features.get(
                "microsleep_detected", False
            )

            pitch = self._angle_deviation(
                self._number(features.get("pitch")),
                "pitch_mean",
            )
            yaw = self._angle_deviation(
                self._number(features.get("yaw")),
                "yaw_mean",
            )
            roll = self._angle_deviation(
                self._number(features.get("roll")),
                "roll_mean",
            )

            thresholds = self._thresholds()

            # ---------------------------------------
            # NO FACE / NO EYES
            # ---------------------------------------

            if not face_detected or not eyes_detected:

                if self.missing_start_time is None:
                    self.missing_start_time = current_time

                missing_duration = (
                    current_time -
                    self.missing_start_time
                )

                if missing_duration >= self.missing_timeout:

                    self.state = "UNRESPONSIVE"
                    self.healthy_start_time = None

                return self.state

            else:
                self.missing_start_time = None

            # ---------------------------------------
            # IMMEDIATE UNRESPONSIVE CONDITIONS
            # ---------------------------------------

            if closure_duration >= 4:

                self.state = "UNRESPONSIVE"
                self.healthy_start_time = None

                return self.state

            if microsleep and closure_duration >= 3:

                self.state = "UNRESPONSIVE"
                self.healthy_start_time = None

                return self.state

            # ---------------------------------------
            # DROWSINESS SCORE
            # ---------------------------------------

            score = 0

            if ear > 0 and ear <= thresholds["ear_closed"]:
                score += 2

            # PERCLOS contribution
            if perclos >= thresholds["perclos_drowsy"] + 0.15:
                score += 2

            elif perclos >= thresholds["perclos_drowsy"]:
                score += 1

            # Existing fatigue score
            if fatigue_score > 0.5:
                score += 2

            elif fatigue_score > 0.3:
                score += 1

            # Microsleep contribution
            if microsleep:
                score += 3

            # Closure duration
            if closure_duration >= thresholds["closure_drowsy"] + 0.5:
                score += 2

            elif closure_duration >= thresholds["closure_drowsy"]:
                score += 1

            # Head nodding
            if pitch > 20:
                score += 1

            if pitch > 30:
                score += 2

            # Large head tilt
            if roll > 20:
                score += 1

            # Looking away continuously
            if yaw > 30:
                score += 1

            # Yawning
            if is_yawning:
                score += 1

            if yawn_count >= 3:
                score += 1

            # ---------------------------------------
            # FINAL DECISION
            # ---------------------------------------

            if score >= 6:

                self.state = "DROWSY"
                self.healthy_start_time = None

            elif self.state in {"DROWSY", "UNRESPONSIVE"}:
                if self.healthy_start_time is None:
                    self.healthy_start_time = current_time
                elif current_time - self.healthy_start_time >= self.recovery_time:
                    self.state = "NORMAL"
                    self.healthy_start_time = None
            else:
                self.state = "NORMAL"

            return self.state

        except Exception as e:

            print(
                f"[CLASSIFIER ERROR] {e}"
            )

            return "UNKNOWN"