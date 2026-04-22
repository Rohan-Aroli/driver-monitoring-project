import json
import time
from pathlib import Path
import cv2

from carla_codes.vehicle_functions import set_hazard_lights, honk
import carla_codes.spawn_car_and_camera as cam

# -------------------- PATH --------------------
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "shared" / "driver_state.json"


# -------------------- READ DRIVER STATE --------------------
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


# -------------------- CONTROL LOOP --------------------
def run_control_loop(world, vehicle, traffic_manager, tm_port):
    prev_state = None
    slow_start_time = None

    try:
        while True:
            # 🔥 REQUIRED for synchronous mode
            world.tick()

            driver_state = read_state()

            # ================= NORMAL =================
            if driver_state == "NORMAL":
                if prev_state != "NORMAL":
                    print("🟢 NORMAL → Autopilot ON")

                    vehicle.set_autopilot(True, tm_port)
                    traffic_manager.vehicle_percentage_speed_difference(vehicle, 0)
                    set_hazard_lights(vehicle, False)

                prev_state = "NORMAL"

            # ================= DROWSY =================
            elif driver_state == "DROWSY":
                if prev_state != "DROWSY":
                    print("🟡 DROWSY → Gradual slowdown")

                    vehicle.set_autopilot(True, tm_port)
                    set_hazard_lights(vehicle, True)

                    slow_start_time = time.time()
                    prev_state = "DROWSY"

                elapsed = time.time() - slow_start_time

                # Smooth slowdown via Traffic Manager
                slowdown = min(int(elapsed * 6), 80)
                traffic_manager.vehicle_percentage_speed_difference(vehicle, slowdown)

                # Controlled honk (not spam)
                if int(elapsed) % 3 == 0:
                    print("HONK 🚨")
                    honk()

            # ================= UNRESPONSIVE =================
            elif driver_state == "UNRESPONSIVE":
                if prev_state != "UNRESPONSIVE":
                    print("🔴 UNRESPONSIVE → Emergency mode")

                    vehicle.set_autopilot(False)
                    set_hazard_lights(vehicle, True)

                    for _ in range(3):
                        honk()

                    # TODO: integrate Rohan's module here

                prev_state = "UNRESPONSIVE"

            # ================= UNKNOWN =================
            else:
                print("⚠️ UNKNOWN driver state")

            # ---------------- CAMERA DISPLAY ----------------
            try:
                if cam.latest_frame is not None:
                    cv2.imshow("CARLA Camera", cam.latest_frame)
                    cv2.waitKey(1)
            except Exception as e:
                print("⚠️ Camera error:", e)

    except KeyboardInterrupt:
        print("\n🛑 Control loop stopped")

    except Exception as e:
        print("💥 CONTROL LOOP CRASH:", e)
        raise

    finally:
        print("🧹 Exiting control loop safely")