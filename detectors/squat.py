import math
from core.base_exercise import BaseExercise


class SquatDetector(BaseExercise):
    DOWN_THRESHOLD = 100   
    UP_THRESHOLD = 160     
    MIN_VISIBILITY = 0.7

    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = "start"

    def process(self, landmarks):
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE)
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE)
        )

        left_vis = landmarks[self.LEFT_KNEE].visibility
        right_vis = landmarks[self.RIGHT_KNEE].visibility

        if left_vis >= right_vis:
            knee_angle = left_knee_angle
            hip_idx, knee_idx, ankle_idx, shoulder_idx = self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE, self.LEFT_SHOULDER
        else:
            knee_angle = right_knee_angle
            hip_idx, knee_idx, ankle_idx, shoulder_idx = self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE, self.RIGHT_SHOULDER

        shoulder_pt = self.get_point(landmarks, shoulder_idx)
        hip_pt = self.get_point(landmarks, hip_idx)
        dx = shoulder_pt[0] - hip_pt[0]
        dy = shoulder_pt[1] - hip_pt[1]
        forward_lean_angle = int(math.degrees(math.atan2(abs(dx), abs(dy)))) if dy != 0 else 0

        key_landmark_visible = landmarks[hip_idx].visibility >= self.MIN_VISIBILITY and landmarks[knee_idx].visibility >= self.MIN_VISIBILITY and landmarks[ankle_idx].visibility >= self.MIN_VISIBILITY

        if not key_landmark_visible:
            self.stage = "start"
            return {
                "reps": self.reps,
                "knee_angle": int(knee_angle),
                "back_angle": forward_lean_angle,
                "depth_status": "NO_POSE",
                "form_status": "NO_POSE",
                "state": self.stage,
            }

        if knee_angle <= self.DOWN_THRESHOLD and self.stage in ("start", "up", "rep_complete"):
            self.stage = "down"
        elif knee_angle >= self.UP_THRESHOLD and self.stage == "down":
            self.stage = "up"
            self.reps += 1
            self.stage = "rep_complete"

        if self.stage == "down":
            depth_status = "GOOD DEPTH" if knee_angle <= self.DOWN_THRESHOLD else "TOO HIGH"
        elif self.stage == "up":
            depth_status = "STANDING"
        elif self.stage == "rep_complete":
            depth_status = "REP_COMPLETE"
        elif knee_angle < 135:
            depth_status = "Shallow Squat"
        else:
            depth_status = "STANDING"

        if self.stage == "rep_complete" and knee_angle <= self.DOWN_THRESHOLD:
            self.stage = "down"

        if forward_lean_angle > 35 or knee_angle > 150:
            form_status = "MAJOR"
        elif depth_status in ("Shallow Squat", "TOO HIGH") or forward_lean_angle > 20:
            form_status = "MINOR"
        else:
            form_status = "GOOD"

        return {
            "reps": self.reps,
            "knee_angle": int(knee_angle),
            "back_angle": forward_lean_angle,
            "depth_status": depth_status,
            "form_status": form_status,
            "state": self.stage,
        }
    