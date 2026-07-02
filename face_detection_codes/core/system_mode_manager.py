class SystemModeManager:

    VALID_MODES = [
        "IDLE",
        "CALIBRATION",
        "WAITING",
        "MONITORING",
        "PAUSED",
        "EMERGENCY"
    ]

    def __init__(self):

        self.mode = "IDLE"

        print(
            f"[MODE] Initialized -> {self.mode}"
        )

    # -----------------------------------
    # Set Current Mode
    # -----------------------------------
    def set_mode(self, mode):

        if mode not in self.VALID_MODES:

            raise ValueError(
                f"Invalid mode: {mode}"
            )

        self.mode = mode

        print(
            f"[MODE] Changed -> {self.mode}"
        )

    # -----------------------------------
    # Get Current Mode
    # -----------------------------------
    def get_mode(self):

        return self.mode

    # -----------------------------------
    # Helper Functions
    # -----------------------------------
    def is_idle(self):

        return self.mode == "IDLE"

    def is_calibration(self):

        return self.mode == "CALIBRATION"

    def is_waiting(self):

        return self.mode == "WAITING"

    def is_monitoring(self):

        return self.mode == "MONITORING"

    def is_paused(self):

        return self.mode == "PAUSED"

    def is_emergency(self):

        return self.mode == "EMERGENCY"