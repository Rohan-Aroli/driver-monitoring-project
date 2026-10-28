from threading import Lock

latest_frame = None
latest_stream_frame = None
frame_lock = Lock()


def send_frame(frame):
    """
    Store latest frame safely.
    """
    global latest_frame

    with frame_lock:
        latest_frame = frame.copy()


def send_stream_frame(frame):
    """Store the newest camera frame for low-latency HTTP streaming."""
    global latest_stream_frame

    with frame_lock:
        latest_stream_frame = frame.copy()


def receive_stream_frame():
    with frame_lock:
        if latest_stream_frame is None:
            return None

        return latest_stream_frame.copy()


def receive_frame():
    """
    Return latest frame safely.
    """
    with frame_lock:
        if latest_frame is None:
            return None

        return latest_frame.copy()