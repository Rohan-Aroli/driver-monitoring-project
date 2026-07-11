from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent

face_python = BASE_DIR / "face_detection_codes" / "facedetection" / "Scripts" / "python.exe"
face_main = BASE_DIR / "face_detection_codes" / "main.py"
communicator_main = BASE_DIR / "arduino" / "main.py"
communicator_python = BASE_DIR / "arduino" / "arduino" / "Scripts" / "python.exe"


# Safety check
if not face_python.exists():
    raise FileNotFoundError(
        f"❌ Face detection env not found:\n{face_python}\n"
        "👉 Run: python setup_face_env.py"
    )
if not face_main.exists():
    raise FileNotFoundError(
        f"❌ Face detection main.py not found:\n{face_main}"
    )
if not communicator_main.exists():
    raise FileNotFoundError(
        f"❌ Arduino communicator main.py not found:\n{communicator_main}"
    )
if not communicator_python.exists():   
    raise FileNotFoundError(
        f"❌ Arduino communicator env not found:\n{communicator_python}\n"
        "👉 Run: python setup_arduino_env.py"
    )