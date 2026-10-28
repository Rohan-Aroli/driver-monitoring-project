import threading
import time


class CameraCapture:
    """Continuously capture the newest camera frame without building a queue."""

    def __init__(self, capture, on_frame=None):
        self.capture = capture
        self.on_frame = on_frame
        self._condition = threading.Condition()
        self._latest_frame = None
        self._frame_id = 0
        self._stopping = threading.Event()
        self._thread = None
        self._last_warning = 0.0

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return

        self._stopping.clear()
        self._thread = threading.Thread(
            target=self._capture_loop,
            name="camera-capture",
            daemon=True,
        )
        self._thread.start()

    def _capture_loop(self):
        while not self._stopping.is_set():
            ret, frame = self.capture.read()
            if not ret or frame is None:
                now = time.monotonic()
                if now - self._last_warning >= 1.0:
                    print("[ERROR] Camera frame not received")
                    self._last_warning = now
                time.sleep(0.01)
                continue

            with self._condition:
                self._latest_frame = frame
                self._frame_id += 1
                self._condition.notify_all()

            if self.on_frame is not None:
                self.on_frame(frame)

    def get_latest(self, last_frame_id=0):
        with self._condition:
            while (
                self._frame_id <= last_frame_id
                and not self._stopping.is_set()
            ):
                self._condition.wait(timeout=0.1)

            if self._latest_frame is None:
                return None, self._frame_id

            return self._latest_frame.copy(), self._frame_id

    def stop(self):
        self._stopping.set()
        with self._condition:
            self._condition.notify_all()

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.0)
