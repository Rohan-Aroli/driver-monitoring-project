import time


class YawnDetector:

    def __init__(
            self,
            mar_threshold=0.6,
            min_yawn_duration=1.0):

        self.mar_threshold = mar_threshold
        self.min_yawn_duration = min_yawn_duration

        # Current mouth state
        self.mouth_open = False
        self.mouth_open_start = None

        # Statistics
        self.yawn_count = 0
        self.yawn_durations = []

        # Current status
        self.is_yawning = False

    def update(self, mar):

        current_time = time.time()

        # -----------------------------------
        # Mouth open
        # -----------------------------------
        if mar > self.mar_threshold:

            if not self.mouth_open:
                self.mouth_open = True
                self.mouth_open_start = current_time

            duration = current_time - self.mouth_open_start

            if duration >= self.min_yawn_duration:
                self.is_yawning = True

        # -----------------------------------
        # Mouth closed
        # -----------------------------------
        else:

            if self.mouth_open:

                duration = (
                    current_time -
                    self.mouth_open_start
                )

                # Valid yawn
                if duration >= self.min_yawn_duration:

                    self.yawn_count += 1
                    self.yawn_durations.append(duration)

                    print(
                        f"[YAWN DETECTED] "
                        f"Duration: {duration:.2f}s"
                    )

                self.mouth_open = False
                self.mouth_open_start = None

            self.is_yawning = False

        avg_duration = (
            sum(self.yawn_durations) /
            len(self.yawn_durations)
            if self.yawn_durations else 0
        )

        current_duration = 0

        if self.mouth_open:
            current_duration = (
                current_time -
                self.mouth_open_start
            )

        return {

            "mar": round(mar, 4),

            "is_yawning": self.is_yawning,

            "current_yawn_duration":
                round(current_duration, 2),

            "yawn_count":
                self.yawn_count,

            "avg_yawn_duration":
                round(avg_duration, 2)
        }