import json
import time
from pathlib import Path
import cv2

from carla_codes.vehicle_functions import set_hazard_lights, honk
from carla_codes.custom_vehicle_physics import EmergencyPullOver
import carla_codes.spawn_car_and_camera as cam


# ---------------- PATH ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "shared" / "driver_state.json"


# ---------------- READ DRIVER STATE ----------------
def read_state():
    try:
        with open(JSON_PATH, "r") as f:
            data = json.load(f)

        state = data.get("driver_state", "UNKNOWN")

        if state not in ["NORMAL", "DROWSY", "UNRESPONSIVE"]:
            return "UNKNOWN"

        return state

    except Exception as e:
        print("⚠️ State read error:", e)
        return "UNKNOWN"


# ---------------- CONTROL LOOP ----------------
def run_control_loop(world, vehicle, traffic_manager, tm_port):
    prev_state = None
    drowsy_start_time = None
    last_honk_time = 0
    emergency_system = EmergencyPullOver(world, vehicle)

    try:
        while True:

            # NO world.tick() → async mode handles it
            driver_state = read_state()

            # ================= NORMAL =================
            if driver_state == "NORMAL":
                if prev_state != "NORMAL":
                    print("🟢 NORMAL → Autopilot ON")

                    vehicle.set_autopilot(True, tm_port)
                    traffic_manager.vehicle_percentage_speed_difference(
                        vehicle, 0
                    )

                    set_hazard_lights(vehicle, False)

                prev_state = "NORMAL"
                drowsy_start_time = None

            # ================= DROWSY =================
            elif driver_state == "DROWSY":

                if prev_state != "DROWSY":
                    print("🟡 DROWSY → Warning mode")

                    set_hazard_lights(vehicle, True)
                    honk()

                    drowsy_start_time = time.time()
                    prev_state = "DROWSY"

                elapsed = time.time() - drowsy_start_time

                # slight slowdown only
                traffic_manager.vehicle_percentage_speed_difference(
                    vehicle, 25
                )

                # honk every 2 sec
                if time.time() - last_honk_time >= 2:
                    honk()
                    last_honk_time = time.time()

                # escalate automatically
            #    if elapsed >= 5:
             #       print("🔴 Drowsy > 5 sec → Escalating to UNRESPONSIVE")
              #      driver_state = "UNRESPONSIVE"

            # ================= UNRESPONSIVE =================
            if driver_state == "UNRESPONSIVE":

                if prev_state != "UNRESPONSIVE":
                    print("🚨 UNRESPONSIVE → Emergency parking")

                    vehicle.set_autopilot(False)
                    set_hazard_lights(vehicle, True)

                    for _ in range(3):
                        honk()
                        time.sleep(0.5)

                    emergency_system.start()

                    if prev_state == "UNRESPONSIVE":
                        emergency_system.run_step()

            # ================= UNKNOWN =================
            elif driver_state == "UNKNOWN":
                print("⚠️ UNKNOWN driver state")

            # ---------------- CAMERA DISPLAY ----------------
            try:
                if cam.latest_frame is not None:
                    cv2.imshow("CARLA Camera", cam.latest_frame)
                    cv2.waitKey(1)
            except Exception as e:
                print("⚠️ Camera error:", e)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🛑 Control loop stopped")

    except Exception as e:
        print("💥 CONTROL LOOP CRASH:", e)
        raise

    finally:
        print("🧹 Exiting control loop safely")