# main.py
import argparse, time
from vision.model_loader import ModelLoader
from vision.camera import Camera
from control.turret_controller import TurretController
from config import MODEL_PATH

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m","--model", default=MODEL_PATH)
    args = parser.parse_args()

    model_loader = ModelLoader(args.model)
    camera = Camera(model_loader)
    camera.start_inference()

    turret = TurretController(camera)
    camera.set_draw_callback(turret.visualize_and_track)

    while True:
        time.sleep(0.05)

if __name__ == "__main__":
    main()
