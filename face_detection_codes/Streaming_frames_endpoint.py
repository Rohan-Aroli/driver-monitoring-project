from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
import frame_bridge
import time

app = FastAPI()


def generate_frames():
    while True:
        try:
            latest_frame = frame_bridge.recieve_frames()

            if latest_frame is None:
                time.sleep(0.1)
                continue

            ret, buffer = cv2.imencode('.jpg', latest_frame)

            if not ret:
                continue

            frame_bytes = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'
                + frame_bytes +
                b'\r\n'
            )

        except Exception as e:
            print(f"[API ERROR] {e}")
            time.sleep(0.1)
            continue

# i will exxplain this part if u want .. but its working  
@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/")
def home():
    return {
        "message": "API running successfully",
        "video_endpoint": "/video_feed"
    }