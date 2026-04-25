import sys

sys.path.append(
    r"B:\CARLA_0.9.13\WindowsNoEditor\PythonAPI\carla"
)

import carla
from agents.navigation.basic_agent import BasicAgent



class EmergencyPullOver:
    def __init__(self, world, vehicle):
        self.world = world
        self.vehicle = vehicle
        self.map = world.get_map()
        self.agent = None
        self.target_location = None
        self.active = False
        self.phase = "APPROACH"

    def start(self):
        self.active = True

        print("🚨 Starting roadside emergency pull over")

        self.agent = BasicAgent(self.vehicle, target_speed=20)

        current_loc = self.vehicle.get_location()

        waypoint = self.map.get_waypoint(
            current_loc,
            project_to_road=True,
            lane_type=carla.LaneType.Driving
        )

        right_lane = waypoint.get_right_lane()

        if right_lane and right_lane.lane_type == carla.LaneType.Driving:
            waypoint = right_lane

        forward_wps = waypoint.next(20.0)

        if not forward_wps:
            print("❌ No forward waypoint found")
            self.active = False
            return

        forward_wp = forward_wps[0]

        transform = forward_wp.transform
        right_vector = transform.get_right_vector()

        target_location = transform.location + (
            right_vector * (forward_wp.lane_width * 0.4)
        )

        self.target_location = target_location
        self.agent.set_destination(self.target_location)

        print("✅ Emergency destination set")

    def run_step(self):
        if not self.active or self.agent is None:
            return

        control = self.agent.run_step()
        control.throttle = min(control.throttle, 0.3)

        current_loc = self.vehicle.get_location()
        distance = current_loc.distance(self.target_location)

        if distance < 6:
            control.brake = 0.4

        if distance < 3:
            self.full_stop()
            return

        self.vehicle.apply_control(control)

    def full_stop(self):
        control = carla.VehicleControl()
        control.throttle = 0
        control.brake = 1.0
        control.steer = 0

        self.vehicle.apply_control(control)

        print("✅ Vehicle safely parked roadside")
        self.active = False