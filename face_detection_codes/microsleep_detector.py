import time


class MicrosleepDetector:

    def __init__(self):

        # Eye closure state
        self.eyes_closed = False
        self.eye_close_start = None

        # Statistics
        self.microsleep_count = 0
        self.microsleep_durations = []

        # Current status
        self.current_closure_duration = 0
        self.microsleep_detected = False

    def update(self, ear, ear_threshold):

        current_time = time.time()

        # ---------------------------------
        # Eyes Closed
        # ---------------------------------
        if ear < ear_threshold:

            if not self.eyes_closed:
                self.eyes_closed = True
                self.eye_close_start = current_time

            self.current_closure_duration = (
                current_time - self.eye_close_start
            )

            # Microsleep detection
            if self.current_closure_duration >= 2.0:
                self.microsleep_detected = True

        # ---------------------------------
        # Eyes Opened Again
        # ---------------------------------
        else:

            if self.eyes_closed:

                duration = (
                    current_time -
                    self.eye_close_start
                )

                # Count only genuine microsleeps
                if duration >= 2.0:

                    self.microsleep_count += 1
                    self.microsleep_durations.append(duration)

                    print(
                        f"[MICROSLEEP DETECTED] "
                        f"Duration: {duration:.2f}s"
                    )

            self.eyes_closed = False
            self.eye_close_start = None
            self.current_closure_duration = 0
            self.microsleep_detected = False

        avg_duration = (
            sum(self.microsleep_durations)
            / len(self.microsleep_durations)
            if self.microsleep_durations else 0
        )

        return {

            "continuous_eye_closure":
                round(
                    self.current_closure_duration,
                    2
                ),

            "microsleep_detected":
                self.microsleep_detected,

            "microsleep_count":
                self.microsleep_count,

            "avg_microsleep_duration":
                round(avg_duration, 2)
        }