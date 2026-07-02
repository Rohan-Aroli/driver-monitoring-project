import time
from collections import deque
from ear_calculator import EARCalculator


class DrowsinessDetector:
    def __init__(self, ear_threshold=0.23, min_blink_duration=0.1):

        # EAR calculator
        self.ear_calculator = EARCalculator()

        # Thresholds
        self.ear_threshold = ear_threshold
        self.min_blink_duration = min_blink_duration

        # Eye state
        self.eye_closed = False
        self.eye_close_start = None

        # Blink tracking
        self.blink_timestamps = deque()
        self.closure_durations = []

        # EAR smoothing
        self.smoothed_ear = None
        self.alpha = 0.3

        # PERCLOS tracking
        self.closed_frames = deque()
        self.total_frames = deque()
        self.window_size = 90   # 🔥 reduced for faster recovery

        # 🔥 Initialize decayed PERCLOS
        self.perclos = 0
        self.open_eye_frames = 0
    # ---------------------------
    # EAR SMOOTHING
    # ---------------------------
    def smooth_ear(self, ear):
        if self.smoothed_ear is None:
            self.smoothed_ear = ear
        else:
            self.smoothed_ear = self.alpha * ear + (1 - self.alpha) * self.smoothed_ear

        return self.smoothed_ear

    # ---------------------------
    # MAIN UPDATE FUNCTION
    # ---------------------------
    def update(self, left_eye_points, right_eye_points):

        try:
            current_time = time.time()

            # ---------------------------
            # STEP 1: EAR
            # ---------------------------
            left_ear = self.ear_calculator.calculate_ear(left_eye_points)
            right_ear = self.ear_calculator.calculate_ear(right_eye_points)

            ear = (left_ear + right_ear) / 2.0
            ear = self.smooth_ear(ear)

            # ---------------------------
            # STEP 2: PERCLOS
            # ---------------------------
            is_closed = ear < self.ear_threshold
            # Track continuous open-eye frames
            if not is_closed:
                self.open_eye_frames += 1
            else:
                self.open_eye_frames = 0

            self.total_frames.append(1)
            self.closed_frames.append(1 if is_closed else 0)

            if len(self.total_frames) > self.window_size:
                self.total_frames.popleft()
                self.closed_frames.popleft()

            raw_perclos = (
                sum(self.closed_frames) / len(self.total_frames)
                if self.total_frames else 0
            )

            # 🔥 DECAY (KEY FIX)
            self.perclos = 0.85 * self.perclos + 0.15 * raw_perclos
            perclos = self.perclos

            # 🔥 HARD RESET if eyes open continuously (~2 sec)
            if self.open_eye_frames > 60:
                self.perclos *= 0.3
                self.closure_durations.clear()

            # ---------------------------
            # STEP 3: BLINK DETECTION
            # ---------------------------
            if is_closed:
                if not self.eye_closed:
                    self.eye_closed = True
                    self.eye_close_start = current_time
            else:
                if self.eye_closed and self.eye_close_start:
                    closure_time = current_time - self.eye_close_start

                    if closure_time >= self.min_blink_duration:
                        self.blink_timestamps.append(current_time)
                        self.closure_durations.append(closure_time)

                    self.eye_closed = False
                    self.eye_close_start = None

            # ---------------------------
            # STEP 4: CLEAN OLD BLINKS
            # ---------------------------
            while self.blink_timestamps:
                if current_time - self.blink_timestamps[0] > 60:
                    self.blink_timestamps.popleft()
                else:
                    break

            blink_rate = len(self.blink_timestamps)

            avg_closure = (
                sum(self.closure_durations) / len(self.closure_durations)
                if self.closure_durations else 0
            )

            # ---------------------------
            # STEP 5: SCORE
            # ---------------------------
            drowsiness_score = (
                (perclos * 0.5) +
                (min(avg_closure, 1.0) * 0.3) +
                (min(blink_rate / 20.0, 1.0) * 0.2)
            )

            return {
                "ear": round(ear, 4),
                "blink_rate": blink_rate,
                "avg_closure_duration": round(avg_closure, 4),
                "perclos": round(perclos, 4),
                "drowsiness_score": round(drowsiness_score, 4)
            }

        except Exception as e:
            print(f"[DROWSINESS ERROR]: {e}")

            return {
                "ear": 0.0,
                "blink_rate": 0,
                "avg_closure_duration": 0.0,
                "perclos": 0.0,
                "drowsiness_score": 0.0,
                "exception": str(e)
            }