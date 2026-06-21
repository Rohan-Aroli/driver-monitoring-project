from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent

face_python = BASE_DIR / "face_detection_codes" / "facedetection" / "Scripts" / "python.exe"
face_main = BASE_DIR / "face_detection_codes" / "main.py"
communicator_main = BASE_DIR / "arduino" / "main.py"
communicator_python = BASE_DIR / "arduino" / "arduino" / "Scripts" / "python.exe"

