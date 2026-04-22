import carla
import math
import sys
sys.path.append(r"C:\Users\aroli\OneDrive\Desktop\final year project\utilities\carla\PythonAPI\carla")
from agents.navigation.basic_agent import BasicAgent


class EmergencyPullOver:
    def __init__(self, world, vehicle):
        self.world = world
        self.vehicle = vehicle
        self.map = world.get_map()

        self.agent = None
        self.target_location = None
        self.active = False

    def start(self):
        """
        Initialize emergency pull-over behavior
        """
        self.active = True

        # 1) Create agent with controlled speed
        self.agent = BasicAgent(self.vehicle, target_speed=20)

        # 2) Get current waypoint (projected to road safely)
        waypoint = self.map.get_waypoint(
            self.vehicle.get_location(),
            project_to_road=True,
            lane_type=carla.LaneType.Driving
        )

        # 3) Shift ONE lane to the right (not extreme edge)
        right_lane = waypoint.get_right_lane()
        if right_lane and right_lane.lane_type == carla.LaneType.Driving:
            waypoint = right_lane

        # 4) Move sufficiently forward (gives planner space)
        next_wps = waypoint.next(30.0)

        if not next_wps:
            # fallback → stay in same lane but move forward
            next_wps = waypoint.next(10.0)

        target_waypoint = next_wps[0]
        self.target_location = target_waypoint.transform.location

        # 5) Explicitly define route (CRITICAL)
        start_location = self.vehicle.get_location()
        self.agent.set_destination(start_location, self.target_location)

        print("🚨 Emergency pull-over started")

    def run_step(self):
        """
        Execute one step of emergency behavior
        """
        if not self.active or self.agent is None:
            return
    

        # Get control from agent
        control = self.agent.run_step()

        # Apply control
        self.vehicle.apply_control(control)

        # Check if near target → stop vehicle
        if self._reached_destination():
            self._full_stop()

    def _get_rightmost_lane(self, waypoint):
        """
        Traverse to rightmost driving lane
        """
        while True:
            right_lane = waypoint.get_right_lane()

            if right_lane is None:
                break

            if right_lane.lane_type != carla.LaneType.Driving:
                break

            waypoint = right_lane

        return waypoint

    def _reached_destination(self):
        """
        Check if vehicle reached target location
        """
        current_loc = self.vehicle.get_location()

        distance = current_loc.distance(self.target_location)

        return distance < 3.0  # threshold in meters

    def _full_stop(self):
        """
        Apply full brake and stop vehicle
        """
        control = carla.VehicleControl()
        control.throttle = 0.0
        control.brake = 1.0
        control.steer = 0.0

        self.vehicle.apply_control(control)

        print("✅ Vehicle safely stopped at roadside")

        self.active = False


