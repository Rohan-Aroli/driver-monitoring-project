import json
import time
import serial

# --------------------------------
# CONFIG
# --------------------------------






def run_arduino_communicator():

    JSON_FILE = r"C:\Users\aroli\OneDrive\Desktop\final year project\driver monitoring\shared\driver_state.json"

    ARDUINO_PORT = "COM8"
    BAUD_RATE = 9600

    # --------------------------------
    # SERIAL
    # --------------------------------

    arduino = serial.Serial(
        ARDUINO_PORT,
        BAUD_RATE
    )

    time.sleep(2)

    print("[INFO] Arduino connected")

    # --------------------------------
    # STATE VARIABLES
    # --------------------------------

    candidate_state = None
    candidate_since = None

    confirmed_state = None
    sent_state = None

    # --------------------------------
    # CONFIRMATION TIMES
    # --------------------------------

    CONFIRMATION_TIME = {
        "NORMAL": 0,
        "DROWSY": 3,
        "UNRESPONSIVE": 3
    }

    print("[INFO] Starting Arduino communicator...")

    while True:

        try:

            with open(JSON_FILE, "r") as f:
                data = json.load(f)

            detected_state = data["driver_state"]

            # ----------------------------
            # NEW CANDIDATE?
            # ----------------------------

            if detected_state != candidate_state:

                candidate_state = detected_state
                candidate_since = time.time()

                print(
                    f"[CANDIDATE] {candidate_state}"
                )

            # ----------------------------
            # CONFIRMATION
            # ----------------------------

            required_time = CONFIRMATION_TIME.get(
                candidate_state,
                3
            )

            if (
                time.time() - candidate_since
                >= required_time
            ):

                if confirmed_state != candidate_state:

                    confirmed_state = candidate_state

                    print(
                        f"[CONFIRMED] {confirmed_state}"
                    )

            # ----------------------------
            # SEND ONLY ON CHANGE
            # ----------------------------

            if (
                confirmed_state is not None
                and confirmed_state != sent_state
            ):

                if confirmed_state == "NORMAL":

                    arduino.write(b'N')

                elif confirmed_state == "DROWSY":

                    arduino.write(b'D')

                elif confirmed_state == "UNRESPONSIVE":

                    arduino.write(b'U')

                sent_state = confirmed_state

                print(
                    f"[SENT] {sent_state}"
                )

        except Exception as e:

            print(
                f"[ERROR] {e}"
            )

        time.sleep(0.1)
