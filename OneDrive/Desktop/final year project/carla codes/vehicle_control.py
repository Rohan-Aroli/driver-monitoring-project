import json
import time

from vehicle_functions import set_hazard_lights, honk
from custom_vehicle_physics import gradual_stop

def read_state():
    try:
        with open(r"C:\Users\aroli\OneDrive\Desktop\final year project\face detection codes\driver_state.json", "r") as f:
            data = json.load(f)
            return data.get("face_detected", True)
    except:
        return False


def run_control_loop(vehicle):

    prev_state = None

    while True:

        face_detected = read_state()

        if face_detected:
            if prev_state != "NORMAL":
                print("Driver detected → Autopilot ON")
                vehicle.set_autopilot(True)
                set_hazard_lights(vehicle, False)

            prev_state = "NORMAL"

        else:
            if prev_state != "UNRESPONSIVE":
                print("Driver missing → Emergency mode")

                vehicle.set_autopilot(False)
                set_hazard_lights(vehicle, True)

                for _ in range(3):
                    honk()

                gradual_stop(vehicle)

            prev_state = "UNRESPONSIVE"

        time.sleep(0.2)