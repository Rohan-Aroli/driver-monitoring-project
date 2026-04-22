import cv2
import time
import json
import os
from datetime import datetime
from pathlib import Path

from face_detection import FaceDetector
from eye_landmark_extractor import EyeLandmarkExtractor
from drowsiness_detector import DrowsinessDetector


# ======================
# CONFIG
# ======================
DURATION = 5  # seconds
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "calibration_data.json"


# ======================
# SAFE JSON APPEND
# ======================
def append_json(entry):
    print("\n🔄 Attempting to save JSON...")

    data = []

    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
                data = json.load(f)
                print(f"📂 Existing entries loaded: {len(data)}")
        except Exception as e:
            print(f"⚠️ JSON read failed, resetting file: {e}")
            data = []

    data.append(entry)

    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Data saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ JSON write failed: {e}")


# ======================
# MAIN TEST FUNCTION
# ======================
def run_calibration(state):

    cap = cv2.VideoCapture(0)

    detector = FaceDetector()
    extractor = EyeLandmarkExtractor()
    drowsy = DrowsinessDetector()

    ear_values = []
    perclos_values = []
    score_values = []

    print(f"\n🔥 Running {state.upper()} calibration for {DURATION} seconds")
    print("👉 Press ESC to stop early\n")

    start = time.time()

    while time.time() - start < DURATION:

        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Camera not returning frame")
            continue

        data = detector.detect(frame)

        if data["face_detected"]:
            x, y, w, h = data["face_bbox"]
            face = frame[y:y+h, x:x+w]

            landmarks = extractor.extract(face, (x, y, w, h))

            left_eye = landmarks["left_eye"]
            right_eye = landmarks["right_eye"]

            if len(left_eye) == 6 and len(right_eye) == 6:

                metrics = drowsy.update(left_eye, right_eye)

                ear = metrics["ear"]
                perclos = metrics["perclos"]
                score = metrics["drowsiness_score"]

                ear_values.append(ear)
                perclos_values.append(perclos)
                score_values.append(score)

                print(
                    f"EAR: {ear:.3f} | "
                    f"PERCLOS: {perclos:.3f} | "
                    f"SCORE: {score:.3f}"
                )

            else:
                print("[WARNING] Eye landmarks incomplete")

        else:
            print("[INFO] Face not detected")

        cv2.imshow("Calibration Tester", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            print("⏹ Stopped by user")
            break

    cap.release()
    cv2.destroyAllWindows()

    # ======================
    # AGGREGATION
    # ======================
    print("\n📊 Aggregating results...")

    if not ear_values:
        print("❌ No valid data collected. Nothing will be saved.")
        return

    entry = {
        "session_id": f"session_{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "state": state,
        "avg_ear": round(sum(ear_values) / len(ear_values), 4),
        "min_ear": round(min(ear_values), 4),
        "max_ear": round(max(ear_values), 4),
        "avg_perclos": round(sum(perclos_values) / len(perclos_values), 4),
        "max_perclos": round(max(perclos_values), 4),
        "avg_score": round(sum(score_values) / len(score_values), 4),
        "max_score": round(max(score_values), 4),
        "samples": len(ear_values),
        "duration_sec": DURATION
    }

    print("\n🧾 Entry to be saved:")
    print(json.dumps(entry, indent=4))

    append_json(entry)


# ======================
# DRIVER
# ======================
if __name__ == "__main__":

    print("\n=== CALIBRATION TESTER ===")
    print("1 → NORMAL")
    print("2 → DROWSY")
    print("3 → UNRESPONSIVE")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        run_calibration("normal")
    elif choice == "2":
        run_calibration("drowsy")
    elif choice == "3":
        run_calibration("unresponsive")
    else:
        print("Invalid choice. Try again.")