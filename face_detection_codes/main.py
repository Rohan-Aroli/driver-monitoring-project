
import cv2
import threading
import uvicorn
import sys
import os

# ---------------- FIX BACKEND IMPORT ----------------
# Adds project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from frame_uploader import upload_driver_frame

# ----------------------------------------------------
from face_detection import FaceDetector
from eye_landmark_extractor import EyeLandmarkExtractor
from drowsiness_detector import DrowsinessDetector
from enhanced_driver_state_classifier import (
    EnhancedDriverStateClassifier
)

from mouth_landmark_extractor import (
    MouthLandmarkExtractor
)

from mar_calculator import MARCalculator

from yawn_detector import YawnDetector

from microsleep_detector import (
    MicrosleepDetector
)

from head_pose_estimator import (
    HeadPoseEstimator
)

from baseline_calibration import (
    BaselineCalibrator
)

from logger import (
    write_state_periodically,
    write_scores_periodically
)

from push_metrics import push_driver_metrics

import Streaming_frames_endpoint as stream
import frame_bridge


# ---------------- INITIALIZE MODULES ----------------
drowsy_detector = DrowsinessDetector()
classifier = EnhancedDriverStateClassifier()

mouth_extractor = MouthLandmarkExtractor()

mar_calculator = MARCalculator()

yawn_detector = YawnDetector()

microsleep_detector = MicrosleepDetector()

head_pose_estimator = HeadPoseEstimator()

calibrator = BaselineCalibrator(
    calibration_time=60
)
if calibrator.load_baseline():
    print("[INFO] Existing baseline loaded")

else:
    print(
        "[INFO] No baseline found. Starting calibration."
    )
cap = cv2.VideoCapture(0)
detector = FaceDetector()
extractor = EyeLandmarkExtractor()
last_uploaded_state = None


# ---------------- START FASTAPI SERVER ----------------
def start_api():
    try:
        print("[INFO] Starting FastAPI streaming server...")

        uvicorn.run(
            stream.app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )

    except Exception as e:
        print(f"[ERROR] API Server failed to start: {e}")


# ---------------- MAIN PIPELINE ----------------
def run_face_detection():
    global last_uploaded_state
    print(" DRIVER MONITORING SYSTEM STARTED")
    

    while True:
        try:
            ret, frame = cap.read()

            if not ret or frame is None:
                print("[ERROR] Camera frame not received")
                continue

            # --------------------------------------------
            # CREATE CLEAN FRAME COPY FOR DASHBOARD STREAM
            # --------------------------------------------
            raw_frame = frame.copy()

            # --------------------------------------------
            # SEND FRAME TO LOCAL FASTAPI STREAM
            # --------------------------------------------
            try:
                frame_bridge.send_frame(raw_frame)
            except Exception as e:
                print(f"[WARNING] Frame streaming failed: {e}")

            # --------------------------------------------
            # FACE DETECTION
            # --------------------------------------------
            data = detector.detect(frame)
            face_detected = data["face_detected"]

            left_eye = []
            right_eye = []
            mouth_points = []

            landmarks = {
                "left_eye": [],
                "right_eye": [],
                "nose_tip": None,
                "chin": None,
                "left_eye_corner": None,
                "right_eye_corner": None,
                "left_mouth_corner": None,
                "right_mouth_corner": None
            }

            x, y, w, h = 0, 0, 0, 0

            # --------------------------------------------
            # EXTRACT EYE LANDMARKS
            # --------------------------------------------
            if face_detected:
                try:
                    x, y, w, h = data["face_bbox"]

                    face_region = frame[y:y+h, x:x+w]

                    landmarks = extractor.extract(
                        face_region,
                        (x, y, w, h)
                    )

                    left_eye = landmarks["left_eye"]
                    right_eye = landmarks["right_eye"]

                    mouth_data = mouth_extractor.extract(
                        face_region,
                        (x, y, w, h)
                    )

                    mouth_points = mouth_data["mouth"]

                except Exception as e:
                    print(f"[ERROR] Landmark extraction failed: {e}")
                    face_detected = False

            # --------------------------------------------
            # CLASSIFICATION PIPELINE
            # --------------------------------------------
            try:

                if face_detected and len(left_eye) == 6 and len(right_eye) == 6:

                    metrics = drowsy_detector.update(
                        left_eye,
                        right_eye
                    )

                    # ---------------------------------
                    # MAR
                    # ---------------------------------

                    mar = 0

                    if len(mouth_points) == 8:

                        mar = mar_calculator.calculate_mar(
                            mouth_points
                        )

                    # ---------------------------------
                    # Yawning
                    # ---------------------------------

                    yawn_metrics = yawn_detector.update(
                        mar
                    )

                    # ---------------------------------
                    # Microsleep
                    # ---------------------------------

                    micro_metrics = microsleep_detector.update(
                        metrics["ear"],
                        drowsy_detector.ear_threshold
                    )

                    # ---------------------------------
                    # Head Pose
                    # ---------------------------------

                    if all([
                        landmarks["nose_tip"],
                        landmarks["chin"],
                        landmarks["left_eye_corner"],
                        landmarks["right_eye_corner"],
                        landmarks["left_mouth_corner"],
                        landmarks["right_mouth_corner"]
                    ]):

                        head_pose = head_pose_estimator.estimate(
                            frame,
                            landmarks
                        )

                    else:

                        head_pose = {
                            "pitch": 0,
                            "yaw": 0,
                            "roll": 0
                        }

                    # ---------------------------------
                    # Merge metrics
                    # ---------------------------------

                    metrics.update({

                        "face_detected": True,

                        "eyes_detected": True,

                        "mar": mar,

                        "is_yawning":
                            yawn_metrics["is_yawning"],

                        "yawn_count":
                            yawn_metrics["yawn_count"],

                        "avg_yawn_duration":
                            yawn_metrics["avg_yawn_duration"],

                        "continuous_eye_closure":
                            micro_metrics[
                                "continuous_eye_closure"
                            ],

                        "microsleep_detected":
                            micro_metrics[
                                "microsleep_detected"
                            ],

                        "microsleep_count":
                            micro_metrics[
                                "microsleep_count"
                            ],

                        "pitch":
                            head_pose["pitch"],

                        "yaw":
                            head_pose["yaw"],

                        "roll":
                            head_pose["roll"]
                    })

                    # ---------------------------------
                    # Calibration
                    # ---------------------------------

                    if not calibrator.calibrated:

                        calibrator.update(metrics)

                        driver_state = "CALIBRATING"

                    else:

                        driver_state = classifier.classify(
                            metrics
                        )

                    write_scores_periodically(metrics)

                    # --------------------------------------------
                    # UPLOAD ONLY WHEN DRIVER BECOMES UNRESPONSIVE
                    # --------------------------------------------
                    frame_url = None

                    if (
                        driver_state == "UNRESPONSIVE"
                        and last_uploaded_state != "UNRESPONSIVE"
                    ):
                        frame_url = upload_driver_frame(raw_frame)

                        print(
                            "[INCIDENT SNAPSHOT SAVED]"
                        )

                    last_uploaded_state = driver_state



                    # --------------------------------------------
                    # PUSH METRICS + FRAME URL
                    # --------------------------------------------
                    push_driver_metrics(
                        metrics,
                        driver_state,
                        frame_url
                    )

                elif face_detected:
                    print("[WARNING] Eye landmarks incomplete")

                    metrics = {

                        "face_detected": True,

                        "eyes_detected": False,

                        "drowsiness_score": 0,

                        "perclos": 0,

                        "ear": 0,

                        "blink_rate": 0,

                        "avg_closure_duration": 0,

                        "mar": 0,

                        "yawn_count": 0,

                        "is_yawning": False,

                        "continuous_eye_closure": 0,

                        "microsleep_detected": False,

                        "pitch": 0,

                        "yaw": 0,

                        "roll": 0
                    }
                    driver_state = classifier.classify(metrics)

                    #frame_url = upload_driver_frame(raw_frame)


                    push_driver_metrics(
                        metrics,
                        driver_state,
                        frame_url
                    )

                else:
                    print("[INFO] Face not detected")

                    metrics = {

                        "face_detected": False,

                        "eyes_detected": False,

                        "drowsiness_score": 0,

                        "perclos": 0,

                        "ear": 0,

                        "blink_rate": 0,

                        "avg_closure_duration": 0,

                        "mar": 0,

                        "yawn_count": 0,

                        "is_yawning": False,

                        "continuous_eye_closure": 0,

                        "microsleep_detected": False,

                        "pitch": 0,

                        "yaw": 0,

                        "roll": 0
                    }

                    driver_state = classifier.classify(metrics)

                    #frame_url = upload_driver_frame(raw_frame)

                    push_driver_metrics(
                        metrics,
                        driver_state,
                        frame_url
                    )

            except Exception as e:
                print(f"[ERROR] Classification pipeline failed: {e}")
                driver_state = "ERROR"

            # --------------------------------------------
            # LOG FINAL STATE
            # --------------------------------------------
            try:
                write_state_periodically({
                    "driver_state": driver_state
                })

            except Exception as e:
                print(f"[WARNING] JSON logging failed: {e}")

            print(f"[STATE] {driver_state}")

            # --------------------------------------------
            # LOCAL DEBUG WINDOW
            # --------------------------------------------
            if face_detected:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"STATE: {driver_state}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"EAR: {metrics.get('ear', 0):.2f}",
                    (x, y + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"PERCLOS: {metrics.get('perclos', 0):.2f}",
                    (x, y + h + 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    f"MAR: {metrics.get('mar',0):.2f}",
                    (x, y + h + 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,255,255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Yawns: {metrics.get('yawn_count',0)}",
                    (x, y + h + 95),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255,255,0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Closure: {metrics.get('continuous_eye_closure',0):.1f}s",
                    (x, y + h + 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,255,0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Pitch: {metrics.get('pitch',0):.1f}",
                    (x, y + h + 145),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,0,255),
                    2
                )

                for (lx, ly) in landmarks["left_eye"]:
                    cv2.circle(
                        frame,
                        (lx, ly),
                        3,
                        (0, 0, 255),
                        -1
                    )

                for (rx, ry) in landmarks["right_eye"]:
                    cv2.circle(
                        frame,
                        (rx, ry),
                        3,
                        (255, 0, 0),
                        -1
                    )

                for (mx, my) in mouth_points:
                    cv2.circle(
                        frame,
                        (mx, my),
                        3,
                        (0, 255, 255),
                        -1
                    )

            else:
                cv2.putText(
                    frame,
                    f"STATE: {driver_state}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            cv2.imshow("Driver Monitoring System", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                print("[INFO] Exiting system...")
                break

        except Exception as e:
            print(f"[CRITICAL ERROR] Main loop failure: {e}")
            continue

    cap.release()
    cv2.destroyAllWindows()


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    try:
        threading.Thread(
            target=start_api,
            daemon=True
        ).start()

        run_face_detection()

    except KeyboardInterrupt:
        print("[INFO] System stopped manually")

    except Exception as e:
        print(f"[CRITICAL ERROR] System startup failed: {e}")
