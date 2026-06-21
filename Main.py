import sys
import time
import threading

# from carla_codes.main import run_carla
from subprocess_launcher import start_face_detection, stop_face_detection, start_communicator, stop_communicator


def main():
    print("🚀 Starting Driver Monitoring System")

    try:
        start_face_detection()
        print("Waiting for face detection to initialize...")
        time.sleep(2)  # Give face detection a moment to initialize
        start_communicator()

        # 🔥 Keep CARLA running continuously
        # while True:
            # run_carla()
            # print("⚠️ CARLA exited unexpectedly. Restarting...")
            # time.sleep(2)
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Ctrl+C detected. Shutting down...")

    except Exception as e:
        print("💥 MAIN SYSTEM ERROR:", e)

    finally:
        
        stop_face_detection()
        print("🧹 Cleanup done. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()