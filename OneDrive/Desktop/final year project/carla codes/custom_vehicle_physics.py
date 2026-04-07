import carla
from vehicle_functions import set_hazard_lights, honk


def gradual_stop(vehicle):
    vehicle.set_autopilot(False)

    velocity = vehicle.get_velocity()
    speed = (velocity.x**2 + velocity.y**2 + velocity.z**2) ** 0.5

    while speed > 0.1:
        control = carla.VehicleControl()
        control.throttle = 0.0
        control.brake = min(1.0, speed / 10)  # proportional braking

        vehicle.apply_control(control)

        velocity = vehicle.get_velocity()
        speed = (velocity.x**2 + velocity.y**2 + velocity.z**2) ** 0.5
    
