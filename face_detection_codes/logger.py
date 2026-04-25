import json
import time
from pathlib import Path

# Universal root path
BASE_DIR = Path(__file__).resolve().parent.parent

# Shared folder paths
STATE_JSON_PATH = BASE_DIR / "shared" / "driver_state.json"
SCORES_JSON_PATH = BASE_DIR / "shared" / "all_scores.json"

# Write timers
last_state_write = 0
last_score_write = 0

STATE_WRITE_INTERVAL = 1.0     # seconds
SCORE_WRITE_INTERVAL = 0.5     # seconds


# -----------------------------------
# Driver state logger
# -----------------------------------
def write_state_periodically(data):
    global last_state_write

    current_time = time.time()

    if current_time - last_state_write < STATE_WRITE_INTERVAL:
        return

    last_state_write = current_time

    STATE_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(STATE_JSON_PATH, "w") as f:
            json.dump(data, f, indent=4)
            f.flush()

        print(f"[STATE LOGGER] {data}")

    except Exception as e:
        print(f"[STATE LOGGER ERROR]: {e}")


# -----------------------------------
# Drowsiness metrics logger
# -----------------------------------
def write_scores_periodically(metrics):
    global last_score_write

    current_time = time.time()

    if current_time - last_score_write < SCORE_WRITE_INTERVAL:
        return

    last_score_write = current_time

    SCORES_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(SCORES_JSON_PATH, "w") as f:
            json.dump(metrics, f, indent=4)
            f.flush()

        print(f"[SCORE LOGGER] {metrics}")

    except Exception as e:
        print(f"[SCORE LOGGER ERROR]: {e}")