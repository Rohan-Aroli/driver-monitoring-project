import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "shared" / "driver_state.json"

last_write_time = 0
WRITE_INTERVAL = 0.5  # seconds

def write_state_periodically(face_detected):
    global last_write_time
    
    current_time = time.time()
    
    if current_time - last_write_time >= WRITE_INTERVAL:
        data = {
                "face_detected": face_detected,
            }
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with open(JSON_PATH, "w") as f:
            json.dump(data, f)
        
        last_write_time = current_time