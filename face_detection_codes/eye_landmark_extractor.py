import cv2
import mediapipe as mp
from logger import write_state_periodically

LEFT_EYE = [
33, 160, 158, 133, 153, 144,
163, 7, 246, 161, 159, 157,
173, 155, 154, 145
]

RIGHT_EYE = [
362, 385, 387, 263, 373, 380,
390, 249, 466, 388, 386, 384,
398, 382, 381, 374
]

class EyeLandmarkExtractor:

    def __init__(self):

        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract(self,face,bbox_values):
        

        if face is None:
             return {
                "left_eye": [],
                "right_eye": []
            }
        x,y,w,h=bbox_values
        

        rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)

        results = self.face_mesh.process(rgb)

        left_eye_points = []
        right_eye_points = []

        if results.multi_face_landmarks:

            face_landmarks = results.multi_face_landmarks[0]

            landmarks = face_landmarks.landmark

            for idx in LEFT_EYE:
                lm = landmarks[idx]

                px = int(lm.x * w) + x
                py = int(lm.y * h) + y

                left_eye_points.append((px, py))

            for idx in RIGHT_EYE:
                lm = landmarks[idx]

                px = int(lm.x * w) + x
                py = int(lm.y * h) + y

                right_eye_points.append((px, py))

        return {
            "left_eye": left_eye_points,
            "right_eye": right_eye_points
        }