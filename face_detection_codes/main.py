import cv2

from face_detection import FaceDetector
from logger import write_state_periodically
from eye_landmark_extractor import EyeLandmarkExtractor ###

global prev_x 
global prev_area 
global face_region



POSITION_THRESHOLD = 80
AREA_THRESHOLD = 5000

cap = cv2.VideoCapture(0)
detector = FaceDetector()
extractor = EyeLandmarkExtractor()  ###



eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml'
)

def run_face_detection():

    # prev_x = None
    # prev_area = None
    face_region=None

    print("🔥 FACE DETECTION SCRIPT STARTED")


    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data = detector.detect(frame)

        face_detected = data["face_detected"]

        if face_detected:
            x, y, w, h = data["face_bbox"]
            bbox_values=(x,y,w,h)
            face_region = frame[y:y+h, x:x+w]
            landmarks = extractor.extract(face_region,bbox_values)
        else:
            pass#to be completed

        
        write_state_periodically(landmarks=landmarks)

            
        # else:
        #     pass 
        #to be called inside ridas folder
            
             

        # 🔥 WRITE ONLY VALIDATED RESULT
        # write_state_periodically(face_detected)

        # ---- DRAWING ----
        if face_detected:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "VALID FACE", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            for (lx, ly) in landmarks["left_eye"]:
                cv2.circle(frame, (lx, ly), 3, (0,0,255), -1)

            for (rx, ry) in landmarks["right_eye"]:
                cv2.circle(frame, (rx, ry), 3, (255,0,0), -1)

        else:
            cv2.putText(frame, "NO VALID FACE", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            cv2.putText(frame, "NO LANDMARKS EXTRACTED", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_face_detection()
