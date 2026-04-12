import threading
import sys
from carla_codes.main import run_carla
from subprocess_launcher import start_face_detection, stop_face_detection


def main():
    print("🚀 Starting Driver Monitoring System")

    try:
        start_face_detection()   # subprocess
        run_carla()              # main process

    except KeyboardInterrupt:
        print("\n Ctrl+C detected. Shutting down...")

    finally:
        stop_face_detection()
        sys.exit(0)

if __name__ == "__main__":
    main()