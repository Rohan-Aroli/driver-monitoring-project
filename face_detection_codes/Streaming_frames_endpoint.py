from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
import frame_bridge
import time



app = FastAPI()

def generate_frames():
    latest_frame

    while True:
        latest_frame = frame_bridge.recieve_frames()
        if latest_frame is None:
            time.sleep(0.1)
            continue

        ret, buffer = cv2.imencode('.jpg', latest_frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/")
def video_feed():
    return StreamingResponse(generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame")