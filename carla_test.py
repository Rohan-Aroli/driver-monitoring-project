import carla
import time

client = carla.Client("localhost", 2000)
client.set_timeout(10.0)

world = client.get_world()
blueprint_library = world.get_blueprint_library()

# Spawn vehicle
vehicle_bp = blueprint_library.filter("vehicle.*")[0]
spawn_point = world.get_map().get_spawn_points()[0]

vehicle = world.spawn_actor(vehicle_bp, spawn_point)

print("Vehicle spawned")

# AUTOPILOT ONLY (NO TM PORT, NO SYNC, NO NOTHING)
vehicle.set_autopilot(True)

print("Autopilot ON")

while True:
    time.sleep(1)