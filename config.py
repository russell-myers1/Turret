import os

# Default model path (relative to project root)
MODEL_PATH = "/usr/share/hailo-models/yolov8s_pose_h8.hef"



# PID / Filter gains
SOME_GAIN = 0.15           # too high causes drift / large swings
TILT_GAIN = 0.14
DEAD_BAND = 25
TILT_DEAD_BAND = 50
UPDATE_INTERVAL = 0.05  #was 0.8
alpha = 0.8               # too high = jitter
tilt_alpha = 0.5
prediction_offset = 0.25  # how far ahead to predict

# Arduino serial
ARDUINO_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

# Blaster
BLASTER_PORT = '/dev/ttyACM1'
SHOT_COOLDOWN = 2
