import carla
import numpy as np

latest_frame = None


def setup_carla(client):
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    # 🔥 SYNCHRONOUS MODE
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    # Spawn vehicle
    vehicle_bp = blueprint_library.filter('vehicle.*')[0]
    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle = world.spawn_actor(vehicle_bp, spawn_point)

    # Camera
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '640')
    camera_bp.set_attribute('image_size_y', '480')

    camera_transform = carla.Transform(
        carla.Location(x=-5.0, z=2.5),
        carla.Rotation(pitch=-10)
    )

    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    return world, vehicle, camera


def start_camera_stream(camera):
    def process_image(image):
        global latest_frame

        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        latest_frame = array[:, :, :3]

    camera.listen(process_image)