from spawn_car_and_camera import setup_carla, start_camera_stream
from vehicle_control import read_state, run_control_loop

def main():

    vehicle, camera = setup_carla()

    start_camera_stream(camera)

    print("System running...")

    try:
        run_control_loop(vehicle)

    except KeyboardInterrupt:
        print("Stopping system...")


if __name__ == "__main__":
    main()