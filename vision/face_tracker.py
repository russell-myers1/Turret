# vision/face_tracker.py
import time
from collections import deque
from config import *

class FaceTracker:
    def __init__(self):
        # PAN state
        self.filtered_offset = 0
        self.cumulative_target = 0
        self.last_update_time = 0
        self.position_history = deque(maxlen=5)
        self.time_history = deque(maxlen=5)
        # TILT state
        self.filtered_offset_tilt = 0
        self.cumulative_target_tilt = 0
        self.last_update_time_tilt = 0
        self.position_history_tilt = deque(maxlen=5)
        self.time_history_tilt = deque(maxlen=5)

    # === EXACT logic from your old code ===
    def send_combined_pan_tilt(self, cx, cy, frame_width, frame_height):
        now = time.time()

        # PAN
        self.position_history.append(cx)
        self.time_history.append(now)
        if len(self.position_history) >= 2:
            dx = self.position_history[-1] - self.position_history[-2]
            dt = self.time_history[-1] - self.time_history[-2]
            velocity_x = dx / dt if dt > 0 else 0
            predicted_x = cx + velocity_x * prediction_offset
            raw_x = predicted_x - (frame_width / 2)
            self.filtered_offset = alpha * raw_x + (1 - alpha) * self.filtered_offset
            if abs(self.filtered_offset) >= DEAD_BAND:
                delta_x = int(self.filtered_offset * SOME_GAIN)
                self.cumulative_target += delta_x
                self.last_update_time = now

        # TILT
        self.position_history_tilt.append(cy)
        self.time_history_tilt.append(now)
        if len(self.position_history_tilt) >= 2:
            dy = self.position_history_tilt[-1] - self.position_history_tilt[-2]
            dt = self.time_history_tilt[-1] - self.time_history_tilt[-2]
            velocity_y = dy / dt if dt > 0 else 0
            predicted_y = cy + velocity_y * prediction_offset
            raw_y = (frame_height / 2) - predicted_y
            self.filtered_offset_tilt = tilt_alpha * raw_y + (1 - tilt_alpha) * self.filtered_offset_tilt
            if abs(self.filtered_offset_tilt) >= TILT_DEAD_BAND:
                delta_y = int(self.filtered_offset_tilt * TILT_GAIN)
                self.cumulative_target_tilt += delta_y
                self.last_update_time_tilt = now

        # return the absolute cumulative targets (same as old)
        return self.cumulative_target, self.cumulative_target_tilt
