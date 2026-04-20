import numpy as np

class EARCalculator:

    def _distance(self, p1, p2):
        try:
            return np.linalg.norm(np.array(p1) - np.array(p2))
        except Exception:
            return 0.0

    def calculate_ear(self, eye_points):
        """
        eye_points: list of 6 eye landmarks [(x,y), ...]
        """

        try:
            if eye_points is None:
                raise ValueError("eye_points is None")

            if not isinstance(eye_points, (list, tuple)):
                raise TypeError("eye_points must be list/tuple")

            if len(eye_points) != 6:
                raise ValueError("eye_points must contain exactly 6 points")

            for p in eye_points:
                if not isinstance(p, (list, tuple)) or len(p) != 2:
                    raise ValueError("Each point must be (x, y)")

            p1, p2, p3, p4, p5, p6 = eye_points

            horizontal = self._distance(p1, p4)
            vertical_1 = self._distance(p2, p6)
            vertical_2 = self._distance(p3, p5)

            if horizontal == 0:
                return 0.0

            ear = (vertical_1 + vertical_2) / (2.0 * horizontal)

            if np.isnan(ear) or np.isinf(ear):
                return 0.0

            return float(ear)

        except Exception as e:
            print(f"[EAR ERROR]: {e}")
            return 0.0