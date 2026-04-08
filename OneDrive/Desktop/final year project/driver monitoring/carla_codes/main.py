from carla_codes.spawn_car_and_camera import setup_carla, start_camera_stream
from carla_codes.vehicle_control import read_state, run_control_loop
import subprocess
import time
import socket

def is_carla_running(host="localhost", port=2000):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except:
        return False

def start_carla_if_needed():
    if not is_carla_running():
        print("🚀 Starting CARLA simulator...")

        subprocess.Popen([
    r"C:\Users\aroli\OneDrive\Desktop\final year project\utilities\carla\CarlaUE4.exe",
    "-windowed",
    "-ResX=800",
    "-ResY=600",
    "-dx11",
    "-quality-level=Low"
])

        print("⏳ Waiting for CARLA to be ready...")

        # 🔥 wait loop instead of sleep
        print("⏳ Waiting 45 seconds for CARLA to fully load...")
        time.sleep(45)


    else:
        print("✅ CARLA already running")


def run_carla():

    start_carla_if_needed()

    vehicle, camera = setup_carla()

    start_camera_stream(camera)

    print("System running...")

    try:
        run_control_loop(vehicle)

    except KeyboardInterrupt:
        print("Stopping system...")


if __name__ == "__main__":
    run_carla()