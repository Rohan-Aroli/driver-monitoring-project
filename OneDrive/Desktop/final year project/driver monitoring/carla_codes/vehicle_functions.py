import carla

def set_hazard_lights(vehicle, state=True):
    lights = carla.VehicleLightState.Position | carla.VehicleLightState.LowBeam
    
    if state:
        lights |= carla.VehicleLightState.LeftBlinker
        lights |= carla.VehicleLightState.RightBlinker
    
    vehicle.set_light_state(carla.VehicleLightState(lights))

def honk():
    print("HONK 🚨")