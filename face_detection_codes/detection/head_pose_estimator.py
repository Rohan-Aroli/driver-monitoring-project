import cv2
import numpy as np


class HeadPoseEstimator:

    def estimate(
            self,
            image,
            landmarks):

        try:

            image_points = np.array([

                landmarks["nose_tip"],
                landmarks["chin"],
                landmarks["left_eye_corner"],
                landmarks["right_eye_corner"],
                landmarks["left_mouth_corner"],
                landmarks["right_mouth_corner"]

            ], dtype="double")

            h, w = image.shape[:2]

            focal_length = w

            center = (w / 2, h / 2)

            camera_matrix = np.array(
                [
                    [focal_length, 0, center[0]],
                    [0, focal_length, center[1]],
                    [0, 0, 1]
                ],
                dtype="double"
            )

            dist_coeffs = np.zeros((4, 1))

            # Generic 3D face model

            model_points = np.array([

                (0.0, 0.0, 0.0),          # Nose

                (0.0, -330.0, -65.0),     # Chin

                (-225.0, 170.0, -135.0),  # Left eye

                (225.0, 170.0, -135.0),   # Right eye

                (-150.0, -150.0, -125.0), # Left mouth

                (150.0, -150.0, -125.0)   # Right mouth

            ])

            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points,
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            if not success:

                return {
                    "pitch": 0,
                    "yaw": 0,
                    "roll": 0
                }

            rotation_matrix, _ = cv2.Rodrigues(
                rotation_vector
            )

            angles, _, _, _, _, _ = cv2.RQDecomp3x3(
                rotation_matrix
            )

            pitch = angles[0]
            yaw = angles[1]
            roll = angles[2]

            return {

                "pitch": round(float(pitch), 2),

                "yaw": round(float(yaw), 2),

                "roll": round(float(roll), 2)
            }

        except Exception as e:

            print(f"[HEAD POSE ERROR]: {e}")

            return {

                "pitch": 0,

                "yaw": 0,

                "roll": 0
            }