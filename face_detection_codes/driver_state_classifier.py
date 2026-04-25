import time


class DriverStateClassifier:

    def __init__(self):
        # Entry thresholds
        self.drowsy_enter = 0.25
        self.unresponsive_enter = 0.55

        self.drowsy_perclos_enter = 0.25
        self.unresponsive_perclos_enter = 0.75

        # Exit thresholds
        self.drowsy_exit = 0.15
        self.unresponsive_exit = 0.4

        self.drowsy_perclos_exit = 0.1
        self.unresponsive_perclos_exit = 0.5

        self.state = "NORMAL"

        # Missing detection tracking
        self.missing_start_time = None
        self.missing_timeout = 4   # seconds (between 3-5 sec)

    def classify(self, metrics):
        try:
            score = metrics.get("drowsiness_score", 0)
            perclos = metrics.get("perclos", 0)

            face_detected = metrics.get("face_detected", True)
            eyes_detected = metrics.get("eyes_detected", True)

            current_time = time.time()

            # ----------------------------------------
            # HANDLE NO FACE / NO EYES
            # ----------------------------------------
            if not face_detected or not eyes_detected:

                if self.missing_start_time is None:
                    self.missing_start_time = current_time
                    print("[WARNING] Face/Eyes missing timer started")

                missing_duration = current_time - self.missing_start_time
                print(f"[INFO] Missing duration: {missing_duration:.2f}s")

                if missing_duration >= self.missing_timeout:
                    self.state = "UNRESPONSIVE"
                    print("[ALERT] Driver missing too long → UNRESPONSIVE")

                return self.state

            else:
                # Reset timer if recovered
                self.missing_start_time = None

            # ----------------------------------------
            # RECOVERY TO NORMAL
            # ----------------------------------------
            if score < 0.2 and perclos < 0.2:
                self.state = "NORMAL"
                return self.state

            # ----------------------------------------
            # NORMAL → DROWSY / UNRESPONSIVE
            # ----------------------------------------
            if self.state == "NORMAL":

                if (
                    score > self.unresponsive_enter and
                    perclos > self.unresponsive_perclos_enter
                ):
                    self.state = "UNRESPONSIVE"

                elif (
                    score > self.drowsy_enter and
                    perclos > self.drowsy_perclos_enter
                ):
                    self.state = "DROWSY"

            # ----------------------------------------
            # DROWSY transitions
            # ----------------------------------------
            elif self.state == "DROWSY":

                if (
                    score > self.unresponsive_enter and
                    perclos > self.unresponsive_perclos_enter
                ):
                    self.state = "UNRESPONSIVE"

                elif (
                    score < self.drowsy_exit and
                    perclos < self.drowsy_perclos_exit
                ):
                    self.state = "NORMAL"

            # ----------------------------------------
            # UNRESPONSIVE recovery
            # ----------------------------------------
            elif self.state == "UNRESPONSIVE":

                if (
                    score < self.unresponsive_exit and
                    perclos < self.unresponsive_perclos_exit
                ):
                    self.state = "DROWSY"

            return self.state

        except Exception as e:
            print(f"[CLASSIFIER ERROR]: {e}")
            return "UNKNOWN"