#!/usr/bin/env python3
"""
Predictive Pan + Tilt Face Tracking using Hailo + Arduino
"""

import argparse
import cv2
import serial
import time
import threading
from collections import deque
from pose_utils import postproc_yolov8_pose
from picamera2 import MappedArray, Picamera2, Preview
from picamera2.devices import Hailo

import serial
import time

# ----------------------------
# Arduino Setup
# ----------------------------
arduino_port = '/dev/ttyACM0'
baud_rate = 115200
arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
#blaster = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)

# Constants

#SOME_GAIN = 0.15
#DEAD_BAND = 50
#UPDATE_INTERVAL = 0.35
#alpha = 0.8
#prediction_offset = 0.1  # Predict 100ms ahea
# ----------------------------
SOME_GAIN = 0.2          #to  high causes drifts/large swings
TILT_GAIN = 0.16
DEAD_BAND = 25            #dead band is too big, small changes in position won’t trigger movement
TILT_DEAD_BAND = 50
UPDATE_INTERVAL = 0.08
alpha = 0.8               #to high can cause jitter(reacts to small movement)
tilt_alpha = 0.5
prediction_offset = 0.25   #frequecy sending coordinates to arduino

# Shared tracking state
filtered_offset = 0
cumulative_target = 0
last_update_time = 0
position_history = deque(maxlen=5)
time_history = deque(maxlen=5)

filtered_offset_tilt = 0
cumulative_target_tilt = 0
last_update_time_tilt = 0
position_history_tilt = deque(maxlen=5)
time_history_tilt = deque(maxlen=5)

# Keypoint index
NOSE, L_EYE, R_EYE, L_EAR, R_EAR = 0, 1, 2, 3, 4

# Prediction shared state
last_predictions = None
prediction_lock = threading.Lock()


last_shot_time = 0
shot_cooldown = 2
'''
def fire_blaster():
    global last_shot_time
    if blaster and time.time() - last_shot_time > shot_cooldown:
        blaster.write(b"FIRE\n")
        blaster.flush()
        last_shot_time = time.time()
        print("Blaster fired")
'''
# ----------------------------
# Combined Pan + Tilt Function
# ----------------------------

def send_combined_pan_tilt(cx, cy, frame_width, frame_height):
    global last_update_time, filtered_offset, cumulative_target
    global last_update_time_tilt, filtered_offset_tilt, cumulative_target_tilt

    now = time.time()

    # PAN
    position_history.append(cx)
    time_history.append(now)
    if len(position_history) >= 2:
        dx = position_history[-1] - position_history[-2]
        dt = time_history[-1] - time_history[-2]
        velocity_x = dx / dt if dt > 0 else 0
        predicted_x = cx + velocity_x * prediction_offset
        raw_x = predicted_x - (frame_width / 2)
        filtered_offset = alpha * raw_x + (1 - alpha) * filtered_offset
        if abs(filtered_offset) >= DEAD_BAND:
            delta_x = int(filtered_offset * SOME_GAIN)
            cumulative_target += delta_x
            last_update_time = now

    # TILT
    position_history_tilt.append(cy)
    time_history_tilt.append(now)
    if len(position_history_tilt) >= 2:
        dy = position_history_tilt[-1] - position_history_tilt[-2]
        dt = time_history_tilt[-1] - time_history_tilt[-2]
        velocity_y = dy / dt if dt > 0 else 0
        predicted_y = cy + velocity_y * prediction_offset
        raw_y = (frame_height / 2) - predicted_y
        filtered_offset_tilt = tilt_alpha * raw_y + (1 - tilt_alpha) * filtered_offset_tilt
        if abs(filtered_offset_tilt) >= TILT_DEAD_BAND:
            delta_y = int(filtered_offset_tilt * TILT_GAIN)
            cumulative_target_tilt += delta_y
            last_update_time_tilt = now

    # COMBINED COMMAND
    if arduino:
        try:
            arduino.write(f"move:{cumulative_target},{cumulative_target_tilt}\n".encode())
        except Exception as e:
            print(f"Error sending combined command: {e}")

# ----------------------------
# Visualize + Control
# ----------------------------
def visualize_face_tracking_result(results, image, model_size,
                                   detection_threshold=0.5, kp_threshold=0.5):
    w, h = image.shape[1], image.shape[0]
    def scale(pt): return (int(pt[0] * w / model_size[0]), int(pt[1] * h / model_size[1]))

    bboxes = results.get('bboxes')
    scores = results.get('scores')
    kps = results.get('keypoints')
    kps_s = results.get('joint_scores')
    if (bboxes is None or len(bboxes) == 0 or
        scores is None or len(scores) == 0 or
        kps is None or len(kps) == 0 or
        kps_s is None or len(kps_s) == 0):
        return

    if scores[0][0] < detection_threshold:
        return

    pts, scores_kp = kps[0][0], kps_s[0][0]
    face_pts = []
    for i in [NOSE, L_EYE, R_EYE, L_EAR, R_EAR]:
        if scores_kp[i] >= kp_threshold:
            raw_pt = pts[i] if hasattr(pts, 'shape') and len(pts.shape) == 2 else pts[2*i:2*i+2]
            face_pts.append(scale(raw_pt))
    if not face_pts:
        return

    xs, ys = zip(*face_pts)
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    cx = (x_min + x_max) // 2
    cy = (y_min + y_max) // 2

    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.putText(image, f"Face {int(scores[0][0]*100)}%", (x_min, y_min-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)

    send_combined_pan_tilt(cx, cy, w, h)
'''
    # Fire if face is roughly centered
    if abs(cx - w/2) < 50 and abs(cy - h/2) < 50:
        fire_blaster()

'''
# ----------------------------
# Draw Callback
# ----------------------------
def draw_predictions(request):
    with MappedArray(request, 'main') as m:
        with prediction_lock:
            preds = last_predictions
        if preds is not None:
            visualize_face_tracking_result(preds, m.array, model_size)

# ----------------------------
# Main
# ----------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--model', default='/usr/share/hailo-models/yolov8s_pose_h8l_pi.hef')
args = parser.parse_args()

with Hailo(args.model) as hailo:
    model_h, model_w, _ = hailo.get_input_shape()
    model_size = (model_w, model_h)
    main_size = (1280, 960)

    with Picamera2() as picam2:
        cfg = picam2.create_video_configuration(
            main={'size': main_size, 'format': 'XRGB8888'},
            lores={'size': model_size, 'format': 'RGB888'}
        )
        picam2.configure(cfg)
         # Start a live preview window
        #picam2.start_preview(Preview.QTGL)
        picam2.start()
        picam2.pre_callback = draw_predictions
        '''
        def inference_loop():
            global last_predictions
            while True:
                frame = picam2.capture_array('lores')
                start = time.time()
                raw = hailo.run(frame)
                preds = postproc_yolov8_pose(1, raw, model_size)
                with prediction_lock:
                    last_predictions = preds
                print(f"Inference time: {time.time() - start:.2f}s")
        '''
        def inference_loop():
            global last_predictions
            frame_count = 0
            DETECTION_INTERVAL = 2   # Only run detection every 2 frames (from normal 16 inferences a sec to 8)
            last_preds = None

            while True:
                frame = picam2.capture_array('lores')
                frame_count += 1

                if frame_count % DETECTION_INTERVAL == 0:
                    start = time.time()
                    raw = hailo.run(frame)
                    preds = postproc_yolov8_pose(1, raw, model_size)
                    last_preds = preds  # save the last valid predictions
                    print(f"Inference time: {time.time() - start:.2f}s")
                else:
                    preds = last_preds   # reuse last detection

                with prediction_lock:
                    last_predictions = preds
                
        threading.Thread(target=inference_loop, daemon=True).start()

        while True:
            time.sleep(0.05)
