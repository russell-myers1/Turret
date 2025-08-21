from picamera2 import Picamera2, MappedArray
import threading
from utils.pose_utils import postproc_yolov8_pose


class Camera:
    def __init__(self, model_loader, main_size=(1280, 960)):
        self.picam2 = Picamera2()
        self.model_loader = model_loader
        self.model_size = model_loader.get_model_size()  # (model_w, model_h)

        # Thread-safe predictions buffer
        self._preds = None
        self._lock = threading.Lock()

        # Optional draw handler (called at camera frame rate)
        self._draw_fn = None

        cfg = self.picam2.create_video_configuration(
            main={'size': main_size, 'format': 'XRGB8888'},
            lores={'size': self.model_size, 'format': 'RGB888'}
        )
        self.picam2.configure(cfg)
        self.picam2.start()

    # ---------- Inference (background thread) ----------
    def start_inference(self):
        def inference_loop():
            frame_count = 0
            DETECTION_INTERVAL = 2  # same cadence as your original script
            last_preds = None

            while True:
                frame = self.picam2.capture_array('lores')
                frame_count += 1

                if frame_count % DETECTION_INTERVAL == 0:
                    raw = self.model_loader.infer(frame)
                    preds = postproc_yolov8_pose(1, raw, self.model_size)
                    last_preds = preds
                else:
                    preds = last_preds  # reuse last valid predictions

                with self._lock:
                    self._preds = preds

        threading.Thread(target=inference_loop, daemon=True).start()

    # ---------- Frame-driven callback (pre_callback) ----------
    def set_draw_callback(self, fn_pred_image):
        """
        Register a function with signature fn_pred_image(preds, image),
        called at camera frame rate from Picamera2's pre_callback.
        """
        self._draw_fn = fn_pred_image

        def _pre_cb(request):
            with self._lock:
                preds = self._preds
            with MappedArray(request, 'main') as m:
                if self._draw_fn is not None:
                    self._draw_fn(preds, m.array)

        self.picam2.pre_callback = _pre_cb

    # ---------- Accessors ----------
    def get_predictions(self):
        with self._lock:
            return self._preds

    def capture_frame(self):
        # Back-compat helper if any code still polls the main stream
        return self.picam2.capture_array()
