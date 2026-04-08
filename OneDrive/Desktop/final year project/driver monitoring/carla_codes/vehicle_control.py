import json
import time
from pathlib import Path


from carla_codes.vehicle_functions import set_hazard_lights, honk
from carla_codes.custom_vehicle_physics import gradual_stop


BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "shared" / "driver_state.json"

def read_state():
    try:
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            return data.get("face_detected", True)
    except:
        return False


def run_control_loop(vehicle):
    try:
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
    except Exception as e:
        print("💥 CONTROL LOOP ERROR:", e)

    time.sleep(0.2)

  