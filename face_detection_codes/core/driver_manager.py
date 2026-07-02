import os


class DriverManager:

    def __init__(self, baseline_folder="baselines"):
        self.current_driver = None
        self.baseline_folder = baseline_folder

        os.makedirs(self.baseline_folder, exist_ok=True)

    def set_driver(self, driver_id):
        self.current_driver = driver_id

    def get_current_driver(self):
        return self.current_driver

    def baseline_exists(self, driver_id):

        path = os.path.join(
            self.baseline_folder,
            f"{driver_id}.json"
        )

        return os.path.exists(path)

    def get_baseline_path(self, driver_id):

        return os.path.join(
            self.baseline_folder,
            f"{driver_id}.json"
        )

    def list_drivers(self):

        drivers = []

        for file in os.listdir(self.baseline_folder):

            if file.endswith(".json"):
                drivers.append(
                    file.replace(".json", "")
                )

        return drivers