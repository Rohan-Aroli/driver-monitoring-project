import json
import time
from pathlib import Path
import carla
import cv2
from carla_codes.vehicle_functions import set_hazard_lights, honk
from carla_codes.custom_vehicle_physics import gradual_stop
import carla_codes.spawn_car_and_camera as cam
from carla_codes.Driver_unresponsive_controls import EmergencyPullOver



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
    emergency_system = EmergencyPullOver(world, vehicle)
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
                
                #if driver_state := "UNRESPONSIVE":
                if prev_state != "UNRESPONSIVE":
                    vehicle.set_autopilot(False)
                    set_hazard_lights(vehicle, True)
                    emergency_system.start()
                    prev_state = "UNRESPONSIVE"
                emergency_system.run_step()
                    
            if cam.latest_frame is not None:
                cv2.imshow("CARLA Camera", cam.latest_frame)
                cv2.waitKey(1)

            # if emergency_active:
                


            time.sleep(0.05)
    except Exception as e:
        print("💥 CONTROL LOOP ERROR:", e)
    
    

    time.sleep(0.2)

  