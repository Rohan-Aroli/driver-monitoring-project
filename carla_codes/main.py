import subprocess
import time
import socket
import carla

from carla_codes.spawn_car_and_camera import setup_carla, start_camera_stream
from carla_codes.vehicle_control import run_control_loop


# -------------------- CHECK CARLA --------------------
def is_carla_running(host="localhost", port=2000):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except:
        return False


# -------------------- START CARLA --------------------
def start_carla_if_needed():
    if not is_carla_running():
        print("🚀 Starting CARLA simulator...")

        subprocess.Popen([
            r"B:\CARLA_0.9.13\WindowsNoEditor\CarlaUE4.exe",
            "-windowed",
            "-ResX=800",
            "-ResY=600",
            "-quality-level=Low"
        ])

    print("⏳ Waiting for CARLA...")

    client = carla.Client("localhost", 2000)
    client.set_timeout(5.0)

    for i in range(80):  # 🔥 increased wait time
        try:
            world = client.get_world()
            if world.get_map() is not None:
                print("✅ CARLA ready")
                return client
        except:
            pass

        print(f"   loading... {i}")
        time.sleep(1)

    raise RuntimeError("CARLA not ready")


# -------------------- MAIN --------------------
def run_carla():
    client = start_carla_if_needed()

    world, vehicle, camera = setup_carla(client)

    # Traffic Manager
    traffic_manager = client.get_trafficmanager()
    traffic_manager.set_synchronous_mode(True)  # 🔥 FIXED

    tm_port = traffic_manager.get_port()

    # Bind vehicle
    vehicle.set_autopilot(True, tm_port)

    start_camera_stream(camera)

    print("🚗 System running...")

    try:
        run_control_loop(world, vehicle, traffic_manager, tm_port)

    finally:
        print("🧹 Cleaning up actors...")

        try:
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