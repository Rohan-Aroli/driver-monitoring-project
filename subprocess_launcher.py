import subprocess
import signal
import sys
import time
from System_paths_config import face_python, face_main , communicator_main, communicator_python
face_process = None




def start_face_detection():
    global face_process

    print("👉 Launching face detection subprocess...")

    

    try:
        face_process = subprocess.Popen(
            [
                face_python,
                face_main
            ],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        # Give it a moment to fail if it's going to
        time.sleep(4)

        if face_process.poll() is not None:
            ###########
            print("❌ Face detection subprocess failed to start.")
            ###########
            raise RuntimeError("Face detection subprocess crashed immediately")

        print("🧠 Face detection subprocess started")

    except Exception as e:
        print(f"❌ Failed to start face detection: {e}")
        face_process = None
        raise




def stop_face_detection():
    global face_process

    if face_process is not None:
        print("🛑 Stopping face detection...")
        face_process.terminate()
        face_process.wait()




def start_communicator():
    print("👉 Launching Arduino Communicator subprocess...")
    try:
        communicator_process = subprocess.Popen(
            [
                communicator_python,
                communicator_main
            ],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        # Give it a moment to fail if it's going to
        time.sleep(4)

        if communicator_process.poll() is not None:
            # print("❌ Arduino Communicator subprocess failed to start.")
            print(f"Exit code: {communicator_process.returncode}")
            raise RuntimeError("Arduino Communicator subprocess crashed immediately")

        print("🛠️ Arduino Communicator subprocess started")
        return communicator_process

    except Exception as e:
        print(f"❌ Failed to start Arduino Communicator: {e}")
        return None




def stop_communicator(communicator_process):
    if communicator_process is not None:
        print("🛑 Stopping Arduino Communicator...")
        communicator_process.terminate()
        communicator_process.wait()