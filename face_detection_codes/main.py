import cv2

from face_detection import FaceDetector
from logger import write_state_periodically
import uvicorn
import threading
import Streaming_frames_endpoint as stream
import frame_bridge

global prev_x 
global prev_area 
global frame_streaming 

POSITION_THRESHOLD = 80
AREA_THRESHOLD = 5000

cap = cv2.VideoCapture(0)
detector = FaceDetector()




eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml'
)

def start_api():
    uvicorn.run(stream.app, host="0.0.0.0", port=8000)

def run_face_detection():
    global frame_streaming
    prev_x = None
    prev_area = None
    print("🔥 FACE DETECTION SCRIPT STARTED")
    

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_streaming = frame
        frame_bridge.send_frames(frame_streaming) ########

        data = detector.detect(frame)

        face_detected = data["face_detected"]

        if face_detected:
            x, y, w, h = data["face_bbox"]

            face_region = frame[y:y+h, x:x+w]

        #check for validation if team wants to 

        else:
            pass
            # final_face = False

        # 🔥 WRITE ONLY VALIDATED RESULT
        write_state_periodically(face_detected=face_detected)

        # ---- DRAWING ----
        if face_detected:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "VALID FACE", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        else:
            cv2.putText(frame, "NO VALID FACE", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start() 
    run_face_detection()

    
