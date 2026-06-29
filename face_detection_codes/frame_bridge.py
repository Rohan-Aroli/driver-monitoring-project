from threading import Lock

latest_frame = None
frame_lock = Lock()


def send_frame(frame):
    """
    Store latest frame safely.
    """
    global latest_frame

    with frame_lock:
        latest_frame = frame.copy()


def receive_frame():
    """
    Return latest frame safely.
    """
    with frame_lock:
        if latest_frame is None:
            return None

        return latest_frame.copy()