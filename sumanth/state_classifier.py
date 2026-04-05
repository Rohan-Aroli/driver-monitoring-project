

class DecisionEngine:
    def __init__(self,
                 ear_threshold=0.25,
                 blink_rate_low=8,
                 blink_rate_high=25):
        """
        ear_threshold: below this → eye considered closed
        blink_rate_low: too low → possible fatigue
        blink_rate_high: too high → abnormal blinking
        dummy thresholds 
        """
        self.ear_threshold = ear_threshold
        self.blink_rate_low = blink_rate_low
        self.blink_rate_high = blink_rate_high

    def classify(self, fatigue_data):
        """
        Input (from Rida):
        {
            "ear": float,
            "blink_rate": float
        }

        Output:
        {
            "state": "NORMAL | DROWSY | UNRESPONSIVE",
            "confidence": float
        }
        """

        if fatigue_data is None:
            return {
                "state": "NO_DATA",
                "confidence": 0.0
            }

        ear = fatigue_data.get("ear", 0)
        blink_rate = fatigue_data.get("blink_rate", 0)

      
        #STATE CLASSIFICATION {WORKING ON A DUMMY VALUE}

        if ear < 0.15:
            state = "UNRESPONSIVE"
            confidence = 0.95

        elif ear < self.ear_threshold or blink_rate < self.blink_rate_low:
            state = "DROWSY"
            confidence = 0.8

        else:
            state = "NORMAL"
            confidence = 0.9

        return {
            "state": state,
            "confidence": confidence
        }
    
    