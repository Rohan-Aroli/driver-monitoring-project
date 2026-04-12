from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent

face_python = BASE_DIR / "face_detection_codes" / "facedetection" / "Scripts" / "python.exe"
face_main = BASE_DIR / "face_detection_codes" / "main.py"

# Safety check
if not face_python.exists():
    raise FileNotFoundError(
        f"❌ Face detection env not found:\n{face_python}\n"
        "👉 Run: python setup_face_env.py"
    )