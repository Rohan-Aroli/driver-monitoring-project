import numpy as np


class MARCalculator:

    def _distance(self, p1, p2):
        try:
            return np.linalg.norm(
                np.array(p1) - np.array(p2)
            )
        except Exception:
            return 0.0

    def calculate_mar(self, mouth_points):
        """
        mouth_points should contain exactly 8 points:

        [
            78,   # Left corner
            81,   # Upper left
            13,   # Upper center
            311,  # Upper right
            308,  # Right corner
            402,  # Lower right
            14,   # Lower center
            178   # Lower left
        ]
        """

        try:

            if mouth_points is None:
                raise ValueError("mouth_points is None")

            if len(mouth_points) != 8:
                raise ValueError(
                    "mouth_points must contain exactly 8 points"
                )

            p1, p2, p3, p4, p5, p6, p7, p8 = mouth_points

            # Horizontal mouth width
            horizontal = self._distance(p1, p5)

            # Vertical distances
            vertical_1 = self._distance(p2, p8)
            vertical_2 = self._distance(p3, p7)
            vertical_3 = self._distance(p4, p6)

            if horizontal == 0:
                return 0.0

            mar = (
                vertical_1 +
                vertical_2 +
                vertical_3
            ) / (3.0 * horizontal)

            if np.isnan(mar) or np.isinf(mar):
                return 0.0

            return float(mar)

        except Exception as e:
            print(f"[MAR ERROR]: {e}")
            return 0.0