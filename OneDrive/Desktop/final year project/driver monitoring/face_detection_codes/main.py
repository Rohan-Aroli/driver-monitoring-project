import cv2

from face_detection import FaceDetector
from logger import write_state_periodically


def run_face_detection():

    prev_x = None
    prev_area = None

    POSITION_THRESHOLD = 80
    AREA_THRESHOLD = 5000

    cap = cv2.VideoCapture(0)
    detector = FaceDetector()



    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_eye.xml'
    )


    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data = detector.detect(frame)

        face_detected = data["face_detected"]

        if face_detected:
            x, y, w, h = data["face_bbox"]

            face_region = frame[y:y+h, x:x+w]

            # ---- VALIDATION START ----
            valid = True

            # 1. Eye check
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY) 
            face_region_gray = gray[y:y+h, x:x+w]

            eyes = eye_cascade.detectMultiScale(face_region_gray)

            # 2. Position consistency
            if valid and prev_x is not None:
                if abs(x - prev_x) > POSITION_THRESHOLD:
                    valid = False

            # 3. Size consistency
            area = w * h
            if valid and prev_area is not None:
                if abs(area - prev_area) > AREA_THRESHOLD:
                    valid = False

            # Update history ONLY if valid
            if valid:
                prev_x = x
                prev_area = area

            final_face = valid

        else:
            final_face = False

        # 🔥 WRITE ONLY VALIDATED RESULT
        write_state_periodically(final_face)

        # ---- DRAWING ----
        if final_face:
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
    run_face_detection()
