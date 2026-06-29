
import cv2
import mediapipe as mp

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Head Pose Landmarks
NOSE_TIP = 1
CHIN = 152

LEFT_EYE_CORNER = 33
RIGHT_EYE_CORNER = 263

LEFT_MOUTH_CORNER = 78
RIGHT_MOUTH_CORNER = 308


class EyeLandmarkExtractor:

    def __init__(self):

        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract(self, face, bbox_values):

        if face is None:
            return {
                "left_eye": [],
                "right_eye": [],
                "nose_tip": None,
                "chin": None,
                "left_eye_corner": None,
                "right_eye_corner": None,
                "left_mouth_corner": None,
                "right_mouth_corner": None
            }

        x, y, w, h = bbox_values

        rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)

        results = self.face_mesh.process(rgb)

        left_eye_points = []
        right_eye_points = []

        nose_tip = None
        chin = None
        left_eye_corner = None
        right_eye_corner = None
        left_mouth_corner = None
        right_mouth_corner = None

        if results.multi_face_landmarks:

            face_landmarks = results.multi_face_landmarks[0]

            landmarks = face_landmarks.landmark

            # Left Eye
            for idx in LEFT_EYE:

                lm = landmarks[idx]

                px = int(lm.x * w) + x
                py = int(lm.y * h) + y

                left_eye_points.append((px, py))

            # Right Eye
            for idx in RIGHT_EYE:

                lm = landmarks[idx]

                px = int(lm.x * w) + x
                py = int(lm.y * h) + y

                right_eye_points.append((px, py))

            # Head Pose Points

            lm = landmarks[NOSE_TIP]
            nose_tip = (
                int(lm.x * w) + x,
                int(lm.y * h) + y
            )

            lm = landmarks[CHIN]
            chin = (
                int(lm.x * w) + x,
                int(lm.y * h) + y
            )

            lm = landmarks[LEFT_EYE_CORNER]
            left_eye_corner = (
                int(lm.x * w) + x,
                int(lm.y * h) + y
            )

            lm = landmarks[RIGHT_EYE_CORNER]
            right_eye_corner = (
                int(lm.x * w) + x,
                int(lm.y * h) + y
            )

            lm = landmarks[LEFT_MOUTH_CORNER]
            left_mouth_corner = (
                int(lm.x * w) + x,
                int(lm.y * h) + y
            )

            lm = landmarks[RIGHT_MOUTH_CORNER]
            right_mouth_corner = (
                int(lm.x * w) + x,
                int(lm.y * h) + y
            )

        return {

            "left_eye": left_eye_points,

            "right_eye": right_eye_points,

            "nose_tip": nose_tip,

            "chin": chin,

            "left_eye_corner": left_eye_corner,

            "right_eye_corner": right_eye_corner,

            "left_mouth_corner": left_mouth_corner,

            "right_mouth_corner": right_mouth_corner
        }

