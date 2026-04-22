class DriverStateClassifier:
    
    def __init__(self):
        # Entry thresholds
        self.drowsy_enter = 0.25
        self.unresponsive_enter = 0.55

        self.drowsy_perclos_enter = 0.25
        self.unresponsive_perclos_enter = 0.75

        # Exit thresholds (lower → recovery)
        self.drowsy_exit = 0.15
        self.unresponsive_exit = 0.4

        self.drowsy_perclos_exit = 0.1
        self.unresponsive_perclos_exit = 0.5
       
        # Current state
        self.state = "NORMAL"

    def classify(self, metrics):
        try:
            score = metrics.get("drowsiness_score", 0)
            perclos = metrics.get("perclos", 0)

            # 🔥 Recovery condition (relaxed)
            if score < 0.2 and perclos < 0.2:
                self.state = "NORMAL"
                return self.state

            # 🔥 State transitions (AND logic)
            if self.state == "NORMAL":
                if score > self.unresponsive_enter and perclos > self.unresponsive_perclos_enter:
                    self.state = "UNRESPONSIVE"
                elif score > self.drowsy_enter and perclos > self.drowsy_perclos_enter:
                    self.state = "DROWSY"

            elif self.state == "DROWSY":
                if score > self.unresponsive_enter and perclos > self.unresponsive_perclos_enter:
                    self.state = "UNRESPONSIVE"
                elif score < self.drowsy_exit and perclos < self.drowsy_perclos_exit:
                    self.state = "NORMAL"

            elif self.state == "UNRESPONSIVE":
                if score < self.unresponsive_exit and perclos < self.unresponsive_perclos_exit:
                    self.state = "DROWSY"

            return self.state

        except Exception as e:
            print(f"[CLASSIFIER ERROR]: {e}")
            return "UNKNOWN"