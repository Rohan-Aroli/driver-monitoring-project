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
        self.phase = "APPROACH"
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

        #******************
        loc = self.vehicle.get_location()

        if loc is None:
            print("❌ Vehicle location not ready")
            return

        waypoint = self.map.get_waypoint(
            loc,
            project_to_road=True,
            lane_type=carla.LaneType.Driving
        #*****************
)

        # 3) Shift ONE lane to the right (not extreme edge)
        right_lane = waypoint.get_right_lane()
        if right_lane and right_lane.lane_type == carla.LaneType.Driving:
            waypoint = right_lane

        # 4) Move sufficiently forward (gives planner space)
        # Step 1: go forward FIRST (important for stability)
        forward_wps = waypoint.next(20.0)

        if not forward_wps:
            return

        forward_wp = forward_wps[0]

        # Step 2: from that point → shift right
        transform = forward_wp.transform
        right_vector = transform.get_right_vector()
        lane_width = forward_wp.lane_width

        offset_distance = lane_width * 0.4

        target_location = transform.location + right_vector * offset_distance
        
        self.target_location = target_location
        self.agent.set_destination(self.target_location)


    def run_step(self):
        """
        Execute one step of emergency behavior
        """
        if not self.active or self.agent is None:
            return
    

        # Get control from agent
        control = self.agent.run_step()

        # limit aggression
        control.throttle = min(control.throttle, 0.3)

        self.vehicle.apply_control(control)

        # Phase switch
        if self.phase == "APPROACH" and self._reached_target_zone(8.0):
            self.phase = "STOPPING"

        # if self.phase == "STOPPING":
        #     control.throttle = 0.0
        #     control.brake = 0.6
        #     self.vehicle.apply_control(control)

        #     if self._reached_target_zone(2.5):
        #         self._full_stop()
        current_loc = self.vehicle.get_location()
        distance = current_loc.distance(self.target_location)
        if self.phase == "STOPPING":
            control = carla.VehicleControl()
            control.throttle = 0.4

            if distance < 6 and distance >= 4:
                control.brake = 0.2
            elif distance < 4 and distance >= 2.5:
                control.brake = 0.4
            else:
                control.brake = 0.8
      
            self.vehicle.apply_control(control)
        # Apply control

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

    def _reached_target_zone(self, threshold=2.5):
        """
        Check if vehicle is within a given distance of target location
        """
        if self.target_location is None:
            return False

        current_loc = self.vehicle.get_location()
        distance = current_loc.distance(self.target_location)

        return distance < threshold

