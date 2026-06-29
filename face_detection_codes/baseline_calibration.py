import time
import json
from pathlib import Path


class BaselineCalibrator:

    def __init__(self, calibration_time=60):

        self.calibration_time = calibration_time

        self.start_time = None

        # Feature buffers
        self.ear_values = []
        self.mar_values = []
        self.perclos_values = []
        self.blink_rates = []
        self.closure_values = []

        self.pitch_values = []
        self.yaw_values = []
        self.roll_values = []

        self.calibrated = False

        self.baseline = {}

        self.save_path = Path(
            "driver_baseline.json"
        )

    # -----------------------------------
    # Start calibration
    # -----------------------------------
    def start(self):

        self.start_time = time.time()

        print(
            "[CALIBRATION] Started"
        )

    # -----------------------------------
    # Update calibration
    # -----------------------------------
    def update(self, metrics):

        if self.calibrated:
            return True

        if self.start_time is None:
            self.start()

        elapsed = (
            time.time() -
            self.start_time
        )

        # Store values

        self.ear_values.append(
            metrics.get("ear", 0)
        )

        self.mar_values.append(
            metrics.get("mar", 0)
        )

        self.perclos_values.append(
            metrics.get("perclos", 0)
        )

        self.blink_rates.append(
            metrics.get("blink_rate", 0)
        )

        self.closure_values.append(
            metrics.get(
                "avg_closure_duration",
                0
            )
        )

        self.pitch_values.append(
            metrics.get("pitch", 0)
        )

        self.yaw_values.append(
            metrics.get("yaw", 0)
        )

        self.roll_values.append(
            metrics.get("roll", 0)
        )

        print(
            f"[CALIBRATING] "
            f"{elapsed:.1f}/"
            f"{self.calibration_time}s"
        )

        # -----------------------------------
        # Calibration completed
        # -----------------------------------
        if elapsed >= self.calibration_time:

            self.baseline = {

                "ear_mean":

                    sum(self.ear_values)
                    / len(self.ear_values),

                "mar_mean":

                    sum(self.mar_values)
                    / len(self.mar_values),

                "perclos_mean":

                    sum(self.perclos_values)
                    / len(self.perclos_values),

                "blink_rate_mean":

                    sum(self.blink_rates)
                    / len(self.blink_rates),

                "closure_mean":

                    sum(self.closure_values)
                    / len(self.closure_values),

                "pitch_mean":

                    sum(self.pitch_values)
                    / len(self.pitch_values),

                "yaw_mean":

                    sum(self.yaw_values)
                    / len(self.yaw_values),

                "roll_mean":

                    sum(self.roll_values)
                    / len(self.roll_values)
            }

            self.save_baseline()

            self.calibrated = True

            print(
                "[CALIBRATION COMPLETE]"
            )

        return self.calibrated

    # -----------------------------------
    # Save baseline
    # -----------------------------------
    def save_baseline(self):

        try:

            with open(
                    self.save_path,
                    "w") as f:

                json.dump(
                    self.baseline,
                    f,
                    indent=4
                )

            print(
                "[BASELINE SAVED]"
            )

        except Exception as e:

            print(
                f"[SAVE ERROR] {e}"
            )

    # -----------------------------------
    # Load baseline
    # -----------------------------------
    def load_baseline(self):

        try:

            with open(
                    self.save_path,
                    "r") as f:

                self.baseline = json.load(f)

            self.calibrated = True

            print(
                "[BASELINE LOADED]"
            )

            return True

        except Exception:

            return False

    # -----------------------------------
    # Get baseline
    # -----------------------------------
    def get_baseline(self):

        return self.baseline