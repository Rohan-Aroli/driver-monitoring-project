from carla_codes.spawn_car_and_camera import setup_carla, start_camera_stream
from carla_codes.vehicle_control import read_state, run_control_loop
import subprocess
import time
import socket
import os


def is_carla_running(host="localhost", port=2000):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except:
        return False

def start_carla_if_needed():
    
    os.system("taskkill /F /IM CarlaUE4.exe")
    time.sleep(3)
    if not is_carla_running():
        print("🚀 Starting CARLA simulator...")

    subprocess.Popen([
    r"C:\Users\aroli\OneDrive\Desktop\final year project\utilities\carla\CarlaUE4.exe",
    "-windowed",
    "-ResX=640",
    "-ResY=480",
    # "-dx11",
    "-quality-level=Low",
    "-fps=15"
    ])

    print("⏳ Waiting for CARLA to be ready...")
    time.sleep(10)

    max_wait = 60
    check_interval = 1
    elapsed = 0

    while elapsed < max_wait:
        if is_carla_running():
            print(f"✅ CARLA ready after {elapsed} seconds")
            time.sleep(2)
            return
        
        print(f"   [{elapsed}s] Waiting for CARLA server...")
        time.sleep(check_interval)
        elapsed += check_interval

    raise TimeoutError("CARLA did not respond...")




def run_carla():

    start_carla_if_needed()

    world,vehicle, camera = setup_carla()

    start_camera_stream(camera)

    print("System running...")

    try:
        run_control_loop(world,vehicle)

    except KeyboardInterrupt:
        print("Stopping system...")
    
    finally:

        print("🧹 Cleaning up actors...")

        try:
            if camera.is_listening:
                camera.stop()
            camera.destroy()
        except:
            pass

        try:
            vehicle.destroy()
        except:
            pass

        import cv2
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_carla()