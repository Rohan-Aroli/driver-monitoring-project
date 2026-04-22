import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "shared" / "driver_state.json"

last_write_time = 0
WRITE_INTERVAL = 1.0  # seconds


def write_state_periodically(data):
    global last_write_time

    current_time = time.time()

    if current_time - last_write_time < WRITE_INTERVAL:
        return

    last_write_time = current_time

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(JSON_PATH, "w") as f:
            json.dump(data, f, indent=4)
            f.flush()

        print(f"[LOGGER] {data}")

    except Exception as e:
        print(f"[LOGGER ERROR]: {e}")