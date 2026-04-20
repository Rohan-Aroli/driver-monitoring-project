import time
from collections import deque
from ear_calculator import EARCalculator


class DrowsinessDetector:
    def __init__(self, ear_threshold=0.23, min_blink_duration=0.1):
        """
        Initializes the drowsiness detection system.

        ear_threshold:
            Threshold below which eye is considered closed.

        min_blink_duration:
            Minimum duration (in seconds) to count as a valid blink.
            Filters out noise / micro eye movements.
        """

        # Module responsible for computing EAR from eye landmarks
        self.ear_calculator = EARCalculator()

        # Detection thresholds
        self.ear_threshold = ear_threshold
        self.min_blink_duration = min_blink_duration

        # ---------------------------
        # Eye State Tracking
        # ---------------------------
        self.eye_closed = False          # Current eye state (open/closed)
        self.eye_close_start = None      # Timestamp when eye closed

        # ---------------------------
        # Blink Tracking
        # ---------------------------
        self.blink_timestamps = deque()  # Stores timestamps of valid blinks (last 60s window)
        self.closure_durations = []      # Stores duration of each blink

        # ---------------------------
        # EAR Smoothing (Noise Reduction)
        # ---------------------------
        self.smoothed_ear = None         # Stores smoothed EAR value
        self.alpha = 0.3                 # EMA smoothing factor (0 < alpha <= 1)

        # ---------------------------
        # PERCLOS Tracking
        # ---------------------------
        self.closed_frames = deque()     # Stores 1 if eye closed, else 0
        self.total_frames = deque()      # Stores total frames count
        self.window_size = 150           # Sliding window (~5 sec at 30 FPS)

    # ---------------------------
    # EAR SMOOTHING FUNCTION
    # ---------------------------
    def smooth_ear(self, ear):
        """
        Applies Exponential Moving Average (EMA) to smooth EAR values.

        Formula:
            smoothed = alpha * current + (1 - alpha) * previous

        Noise reduce karne ke liye from unstable landmark detection.
        """
        if self.smoothed_ear is None:
            self.smoothed_ear = ear
        else:
            self.smoothed_ear = self.alpha * ear + (1 - self.alpha) * self.smoothed_ear

        return self.smoothed_ear

    # ---------------------------
    # MAIN PIPELINE FUNCTION
    # ---------------------------
    def update(self, left_eye_points, right_eye_points):
        """
        Main function me called per frame.

        Input:
            left_eye_points  -> list of 6 (x, y) coordinates
            right_eye_points -> list of 6 (x, y) coordinates

        Output:
            Dictionary containing:
                - EAR
                - Blink rate (per minute)
                - Average blink duration
                - PERCLOS
                - Drowsiness score
        """

        try:
            # Current timestamp for time-based calculations
            current_time = time.time()

            # ---------------------------
            # STEP 1: EAR CALCULATION
            # ---------------------------
            # Convert eye landmarks → EAR values
            left_ear = self.ear_calculator.calculate_ear(left_eye_points)
            right_ear = self.ear_calculator.calculate_ear(right_eye_points)

            # Combine both eyes 
            ear = (left_ear + right_ear) / 2.0  #Avg of both eye onluy if both eye behaviour is symmetrical nhi to doesnt work decide on this

            # Smooth EAR to reduce noise
            ear = self.smooth_ear(ear)

            # ---------------------------
            # STEP 2: PERCLOS (Eye Closure %)
            # ---------------------------
            # Determine if eye is closed

            # Kitne time tak aankh band thi, total time ke comparison me

            is_closed = ear < self.ear_threshold

            # Update sliding window
            self.total_frames.append(1)
            self.closed_frames.append(1 if is_closed else 0)

            # Maintain fixed-size window
            if len(self.total_frames) > self.window_size:
                self.total_frames.popleft()
                self.closed_frames.popleft()

            # Calculate percentage of time eyes are closed
            perclos = (
                sum(self.closed_frames) / len(self.total_frames)
                if self.total_frames else 0
            )

            # ---------------------------
            # STEP 3: BLINK DETECTION
            # ---------------------------

            # Eye just closed → start timing
            if is_closed:
                if not self.eye_closed:
                    self.eye_closed = True
                    self.eye_close_start = current_time

            # Eye just opened → calculate blink duration
            else:
                if self.eye_closed and self.eye_close_start:

                    closure_time = current_time - self.eye_close_start

                    # Ignore very short closures (noise)
                    if closure_time >= self.min_blink_duration:
                        self.blink_timestamps.append(current_time)
                        self.closure_durations.append(closure_time)

                    # Reset state
                    self.eye_closed = False
                    self.eye_close_start = None

            # ---------------------------
            # STEP 4: CLEAN OLD BLINK DATA
            # ---------------------------
            # Keep only last 60 seconds of blink data
            while self.blink_timestamps:
                if current_time - self.blink_timestamps[0] > 60:
                    self.blink_timestamps.popleft()
                else:
                    break

            # Blink rate = number of blinks in last 60 seconds
            blink_rate = len(self.blink_timestamps)

            # Average duration of eye closure
            avg_closure = (
                sum(self.closure_durations) / len(self.closure_durations)
                if self.closure_durations else 0
            )

            # ---------------------------
            # STEP 5: DROWSINESS SCORE
            # ---------------------------
            """
            Heuristic weighted score:
                - PERCLOS (50%) → strongest indicator
                - Closure duration (30%) → longer closures = fatigue
                - Blink rate (20%) → abnormal patterns indicate drowsiness
            """
            drowsiness_score = (
                (perclos * 0.5) +
                (min(avg_closure, 1.0) * 0.3) +
                (min(blink_rate / 30.0, 1.0) * 0.2)
            )

            # ---------------------------
            # OUTPUT
            # ---------------------------
            return {
                "ear": round(ear, 4),
                "blink_rate": blink_rate,
                "avg_closure_duration": round(avg_closure, 4),
                "perclos": round(perclos, 4),
                "drowsiness_score": round(drowsiness_score, 4)
            }

        except Exception as e:
            # Catch unexpected failures (e.g., bad input)
            print(f"[DROWSINESS ERROR]: {e}")

            return {
                "ear": 0.0,
                "blink_rate": 0,
                "avg_closure_duration": 0.0,
                "perclos": 0.0,
                "drowsiness_score": 0.0,
                "exception": str(e)
            }