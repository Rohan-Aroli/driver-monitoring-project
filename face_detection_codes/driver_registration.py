import json
import os


class DriverRegistry:

    def __init__(
            self,
            registry_file="drivers.json"
    ):

        self.registry_file = registry_file

        if not os.path.exists(
                self.registry_file):

            with open(
                    self.registry_file,
                    "w") as f:

                json.dump([], f)

    def get_all_drivers(self):

        with open(
                self.registry_file,
                "r") as f:

            return json.load(f)

    def register_driver(self, driver_id):

        drivers = self.get_all_drivers()

        if driver_id not in drivers:

            drivers.append(driver_id)

            with open(
                    self.registry_file,
                    "w") as f:

                json.dump(
                    drivers,
                    f,
                    indent=4
                )

            print(
                f"[INFO] Registered {driver_id}"
            )

    def delete_driver(self, driver_id):

        drivers = self.get_all_drivers()

        if driver_id in drivers:

            drivers.remove(driver_id)

            with open(
                    self.registry_file,
                    "w") as f:

                json.dump(
                    drivers,
                    f,
                    indent=4
                )

            print(
                f"[INFO] Deleted {driver_id}"
            )