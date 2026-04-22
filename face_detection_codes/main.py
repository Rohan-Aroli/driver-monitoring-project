import cv2

from face_detection import FaceDetector
from logger import write_state_periodically
from eye_landmark_extractor import EyeLandmarkExtractor
from drowsiness_detector import DrowsinessDetector
from driver_state_classifier import DriverStateClassifier

# Initialize modules
drowsy_detector = DrowsinessDetector()
classifier = DriverStateClassifier()

cap = cv2.VideoCapture(0)
detector = FaceDetector()
extractor = EyeLandmarkExtractor()


def run_face_detection():

    print("🔥 FACE DETECTION SCRIPT STARTED")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Camera frame not received")
            break

        data = detector.detect(frame)
        face_detected = data["face_detected"]

        # Default safe values
        left_eye = []
        right_eye = []
        landmarks = {"left_eye": [], "right_eye": []}

        if face_detected:
            try:
                x, y, w, h = data["face_bbox"]
                bbox_values = (x, y, w, h)

                face_region = frame[y:y+h, x:x+w]
                landmarks = extractor.extract(face_region, bbox_values)

                left_eye = landmarks["left_eye"]
                right_eye = landmarks["right_eye"]

            except Exception as e:
                print(f"[ERROR] Landmark extraction failed: {e}")
                face_detected = False  # fallback

        
        # SUMANTH MODULE START

        try:
            if face_detected:
                if len(left_eye) == 6 and len(right_eye) == 6:

                    metrics = drowsy_detector.update(left_eye, right_eye)
                    driver_state = classifier.classify(metrics)

                else:
                    print("[WARNING] Eye landmarks incomplete")
                    driver_state = "NO_EYES"

            else:
                print("[INFO] Face not detected")
                driver_state = "NO_FACE"

        except Exception as e:
            print(f"[ERROR] Pipeline failure: {e}")
            driver_state = "ERROR"

        # Writing ONLY driver_state to JSON
        write_state_periodically({
            "driver_state": driver_state
        })

        # Debug output
        print(f"[STATE] {driver_state}")

        # SUMANTH MODULE END
        

        # ---- DRAWING ----
        if face_detected:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "VALID FACE", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            for (lx, ly) in landmarks["left_eye"]:
                cv2.circle(frame, (lx, ly), 3, (0, 0, 255), -1)

            for (rx, ry) in landmarks["right_eye"]:
                cv2.circle(frame, (rx, ry), 3, (255, 0, 0), -1)

        else:
            cv2.putText(frame, "NO VALID FACE", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, "NO LANDMARKS EXTRACTED", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_face_detection()