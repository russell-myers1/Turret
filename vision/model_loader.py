from picamera2.devices import Hailo

class ModelLoader:
    def __init__(self, hef_path):
        self.hailo = Hailo(hef_path)
        self.model_h, self.model_w, _ = self.hailo.get_input_shape()
        self.model_size = (self.model_w, self.model_h)
        print(f"[ModelLoader] Loaded model {hef_path}")

    def infer(self, frame):
        return self.hailo.run(frame)

    def get_model_size(self):
        return self.model_size
