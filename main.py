import cv2
from face_detection import FaceDetector
from logger import log_every_5_seconds
cap = cv2.VideoCapture(0)
detector = FaceDetector()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    data = detector.detect(frame)

    if data["face_detected"]:
        x, y, w, h = data["face_bbox"]

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, "FACE DETECTED", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    else:
        cv2.putText(frame, "NO FACE", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Face Detection - Rohan Module", frame)
    log_every_5_seconds(data)
    

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()