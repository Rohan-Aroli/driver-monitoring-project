import time


class EnhancedDriverStateClassifier:

    def __init__(self):

        self.state = "NORMAL"

        # Face missing handling
        self.missing_start_time = None
        self.missing_timeout = 4

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

            perclos = features.get(
                "perclos", 0
            )

            fatigue_score = features.get(
                "drowsiness_score", 0
            )

            yawn_count = features.get(
                "yawn_count", 0
            )

            is_yawning = features.get(
                "is_yawning", False
            )

            closure_duration = features.get(
                "continuous_eye_closure", 0
            )

            microsleep = features.get(
                "microsleep_detected", False
            )

            pitch = abs(
                features.get("pitch", 0)
            )

            yaw = abs(
                features.get("yaw", 0)
            )

            roll = abs(
                features.get("roll", 0)
            )

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

                return self.state

            else:
                self.missing_start_time = None

            # ---------------------------------------
            # IMMEDIATE UNRESPONSIVE CONDITIONS
            # ---------------------------------------

            if closure_duration >= 4:

                self.state = "UNRESPONSIVE"

                return self.state

            if microsleep and closure_duration >= 3:

                self.state = "UNRESPONSIVE"

                return self.state

            # ---------------------------------------
            # DROWSINESS SCORE
            # ---------------------------------------

            score = 0

            # PERCLOS contribution
            if perclos > 0.40:
                score += 2

            elif perclos > 0.25:
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
            if closure_duration > 2:
                score += 2

            elif closure_duration > 1:
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

            elif score <= 2:

                self.state = "NORMAL"

            # Hysteresis
            if self.state == "DROWSY":

                if score <= 2:
                    self.state = "NORMAL"

            return self.state

        except Exception as e:

            print(
                f"[CLASSIFIER ERROR] {e}"
            )

            return "UNKNOWN"