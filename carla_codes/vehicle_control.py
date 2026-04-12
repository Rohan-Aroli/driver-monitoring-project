import json
import time
from pathlib import Path
import carla
import cv2

from carla_codes.vehicle_functions import set_hazard_lights, honk
from carla_codes.custom_vehicle_physics import gradual_stop
import carla_codes.spawn_car_and_camera as cam

global emergency_active

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "shared" / "driver_state.json"

def read_state():
    try:
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            return data.get("face_detected", False)
    except:
        return False


def run_control_loop(world,vehicle):
    emergency_active= False
    try:
        prev_state = None

        while True:
            # world.tick()

            face_detected = read_state()

            if face_detected:
                if prev_state != "NORMAL":
                    print("Driver detected → Autopilot ON")
                    vehicle.set_autopilot(True)
                    # print("Autopilot would have been enabled here")
                    set_hazard_lights(vehicle, False)

                prev_state = "NORMAL"

            else:
                if prev_state != "UNRESPONSIVE":
                    print("Driver missing → Emergency mode")

                    vehicle.set_autopilot(False)
                    set_hazard_lights(vehicle, True)

                    for _ in range(3):
                        honk()
                    emergency_active = True

                    # gradual_stop(vehicle)
                    prev_state = "UNRESPONSIVE"
            if cam.latest_frame is not None:
                cv2.imshow("CARLA Camera", cam.latest_frame)
                cv2.waitKey(1)

            if emergency_active:
                control = carla.VehicleControl()
                control.throttle = 0.0
                control.brake = 0.4   

                vehicle.apply_control(control)


            time.sleep(0.05)
    except Exception as e:
        print("💥 CONTROL LOOP ERROR:", e)
    
    

    time.sleep(0.2)

  