import time


class DriverStateClassifier:

    def __init__(self, calibration_profile=None):

        # --------------------------------------------------
        # Driver-specific calibration values
        # --------------------------------------------------

        self.profile = calibration_profile or {
            "baseline_ear": 0.30,
            "baseline_blink_rate": 15,
            "baseline_pitch": -150
        }

        # --------------------------------------------------
        # Current state
        # --------------------------------------------------

        self.state = "NORMAL"

        # --------------------------------------------------
        # Missing face timer
        # --------------------------------------------------

        self.missing_start_time = None
        self.missing_timeout = 5  # seconds

        # --------------------------------------------------
        # Recovery timer
        # --------------------------------------------------

        self.healthy_start_time = None
        self.recovery_time = 2

    # ======================================================
    # Update calibration profile after calibration finishes
    # ======================================================

    def update_profile(self, profile):

        self.profile = profile

        print("\n[INFO] Driver profile updated")
        print(self.profile)

    # ======================================================
    # MAIN CLASSIFIER
    # ======================================================

    def classify(self, metrics):

        try:

            current_time = time.time()

            # ==================================================
            # EXTRACT FEATURES
            # ==================================================

            ear = metrics.get("ear", 0)

            perclos = metrics.get("perclos", 0)

            blink_rate = metrics.get("blink_rate", 0)

            eye_closure = metrics.get(
                "continuous_eye_closure", 0
            )

            is_yawning = metrics.get(
                "is_yawning", False
            )

            yawn_count = metrics.get(
                "yawn_count", 0
            )

            microsleep_detected = metrics.get(
                "microsleep_detected", False
            )

            pitch = metrics.get("pitch", 0)

            yaw = metrics.get("yaw", 0)

            roll = metrics.get("roll", 0)

            face_detected = metrics.get(
                "face_detected", True
            )

            eyes_detected = metrics.get(
                "eyes_detected", True
            )

            # ==================================================
            # LOAD BASELINES
            # ==================================================

            baseline_ear = self.profile.get(
                "baseline_ear", 0.30
            )

            baseline_blink_rate = self.profile.get(
                "baseline_blink_rate", 15
            )

            baseline_pitch = self.profile.get(
                "baseline_pitch", -150
            )

            # ==================================================
            # FACE / EYE MISSING LOGIC
            # ==================================================

            if not face_detected or not eyes_detected:

                if self.missing_start_time is None:
                    self.missing_start_time = current_time

                missing_duration = (
                    current_time -
                    self.missing_start_time
                )

                print(
                    f"[INFO] Face Missing: "
                    f"{missing_duration:.1f}s"
                )

                if missing_duration >= self.missing_timeout:

                    self.state = "UNRESPONSIVE"

                    print(
                        "[ALERT] Driver missing too long"
                    )

                return self.state

            else:
                self.missing_start_time = None

            # ==================================================
            # UNRESPONSIVE DETECTION
            # ==================================================

            if (
                eye_closure >= 5
                or microsleep_detected
            ):

                self.state = "UNRESPONSIVE"

                print(
                    "[ALERT] Driver UNRESPONSIVE"
                )

                return self.state

            # ==================================================
            # FATIGUE SCORE
            # ==================================================

            fatigue_score = 0

            # --------------------------------------------------
            # EAR
            # --------------------------------------------------

            if baseline_ear > 0:

                ear_ratio = ear / baseline_ear

                print(
                    f"[DEBUG] EAR Ratio: "
                    f"{ear_ratio:.2f}"
                )

                if ear_ratio < 0.85:
                    fatigue_score += 2

                if ear_ratio < 0.70:
                    fatigue_score += 1

            # --------------------------------------------------
            # PERCLOS
            # --------------------------------------------------

            if perclos > 0.30:
                fatigue_score += 2

            if perclos > 0.50:
                fatigue_score += 1

            # --------------------------------------------------
            # Blink rate
            # --------------------------------------------------

            if (
                baseline_blink_rate > 0
                and
                blink_rate <
                baseline_blink_rate * 0.5
            ):
                fatigue_score += 1

            # --------------------------------------------------
            # Eye closure
            # --------------------------------------------------

            if eye_closure > 1.5:
                fatigue_score += 2

            # --------------------------------------------------
            # Yawning
            # --------------------------------------------------

            if is_yawning:
                fatigue_score += 2

            if yawn_count >= 3:
                fatigue_score += 1

            # --------------------------------------------------
            # Head Pose Deviation
            # --------------------------------------------------

            pitch_deviation = abs(
                pitch - baseline_pitch
            )

            if pitch_deviation > 15:
                fatigue_score += 1

            if pitch_deviation > 25:
                fatigue_score += 1

            # --------------------------------------------------
            # Microsleep history
            # --------------------------------------------------

            if microsleep_detected:
                fatigue_score += 3

            # ==================================================
            # DISPLAY SCORE
            # ==================================================

            print(
                f"[INFO] Fatigue Score: "
                f"{fatigue_score}"
            )

            # ==================================================
            # FINAL DECISION
            # ==================================================

            if fatigue_score >= 4:

                self.state = "DROWSY"

                self.healthy_start_time = None

            else:

                if self.healthy_start_time is None:
                    self.healthy_start_time = current_time

                healthy_duration = (
                    current_time -
                    self.healthy_start_time
                )

                if healthy_duration >= self.recovery_time:

                    self.state = "NORMAL"

            return self.state

        except Exception as e:

            print(
                f"[CLASSIFIER ERROR]: {e}"
            )

            return "UNKNOWN"