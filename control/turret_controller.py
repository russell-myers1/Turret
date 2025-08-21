# control/turret_controller.py
import cv2
from vision.face_tracker import FaceTracker
from hardware.motor_controller import MotorController

class TurretController:
    def __init__(self, camera):
        self.camera = camera
        self.tracker = FaceTracker()
        self.motors = MotorController()
        self.model_size = self.camera.model_loader.get_model_size()

    def visualize_and_track(self, preds, image, detection_threshold=0.5, kp_threshold=0.5):
        if preds is None:
            return

        w, h = image.shape[1], image.shape[0]
        bboxes = preds.get('bboxes'); scores = preds.get('scores')
        kps = preds.get('keypoints');  kps_s = preds.get('joint_scores')
        if (bboxes is None or len(bboxes) == 0 or
            scores is None or len(scores) == 0 or
            kps is None or len(kps) == 0 or
            kps_s is None or len(kps_s) == 0):
            return
        if scores[0][0] < detection_threshold:
            return

        NOSE, L_EYE, R_EYE, L_EAR, R_EAR = 0, 1, 2, 3, 4
        pts, scores_kp = kps[0][0], kps_s[0][0]

        def scale(pt):
            return (int(pt[0] * w / self.model_size[0]), int(pt[1] * h / self.model_size[1]))

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

        # EXACT call back to your original algorithm
        pan, tilt = self.tracker.send_combined_pan_tilt(cx, cy, w, h)

        # emit the same string as the original
        self.motors.move(pan, tilt)


        # Example: Blaster firing (kept commented)
        # if abs(cx - w/2) < 50 and abs(cy - h/2) < 50:
        #     blaster.fire()
