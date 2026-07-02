import cv2
import mediapipe as mp

# Outer mouth landmarks
MOUTH_LANDMARKS = [
    78,   # Left corner
    81,   # Upper left
    13,   # Upper center
    311,  # Upper right
    308,  # Right corner
    402,  # Lower right
    14,   # Lower center
    178   # Lower left
]


class MouthLandmarkExtractor:

    def __init__(self):

        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,   # Better precision
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract(self, face, bbox_values):

        # Return empty list if face missing
        if face is None:
            return {
                "mouth": []
            }

        x, y, w, h = bbox_values

        rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)

        results = self.face_mesh.process(rgb)

        mouth_points = []

        if results.multi_face_landmarks:

            face_landmarks = results.multi_face_landmarks[0]

            landmarks = face_landmarks.landmark

            for idx in MOUTH_LANDMARKS:

                lm = landmarks[idx]

                px = int(lm.x * w) + x
                py = int(lm.y * h) + y

                mouth_points.append((px, py))

        return {
            "mouth": mouth_points
        }