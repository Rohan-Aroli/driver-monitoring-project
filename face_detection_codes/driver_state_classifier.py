class DriverStateClassifier:
    def __init__(self):
        # Thresholds (we will tune these later)
        self.drowsy_score_threshold = 0.35
        self.unresponsive_score_threshold = 0.65

        self.drowsy_perclos_threshold = 0.3
        self.unresponsive_perclos_threshold = 0.6

    def classify(self, metrics):
        """
        metrics: dict from drowsiness_detector.update()

        Returns:
            driver_state (str)
        """

        try:
            score = metrics.get("drowsiness_score", 0)
            perclos = metrics.get("perclos", 0)

            # 🔥 Decision Logic
            if score > self.unresponsive_score_threshold or perclos > self.unresponsive_perclos_threshold:
                return "UNRESPONSIVE"

            elif score > self.drowsy_score_threshold or perclos > self.drowsy_perclos_threshold:
                return "DROWSY"

            else:
                return "NORMAL"

        except Exception as e:
            print(f"[CLASSIFIER ERROR]: {e}")
            return "UNKNOWN"