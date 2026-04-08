import subprocess
import signal
import sys

face_process = None


def start_face_detection():
    global face_process

    print("👉 Launching face detection subprocess...")

    face_process = subprocess.Popen([
        r"face_detection_codes\facedetection\Scripts\python.exe",
        r"face_detection_codes\main.py"
       
    ],
    creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    print("🧠 Face detection subprocess started")


def stop_face_detection():
    global face_process

    if face_process is not None:
        print("🛑 Stopping face detection...")
        face_process.terminate()
        face_process.wait()