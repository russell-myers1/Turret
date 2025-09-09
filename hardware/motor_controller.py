# hardware/motor_controller.py
# hardware/motor_controller.py
import serial, time
from config import ARDUINO_PORT, BAUD_RATE
from config import SHOT_COOLDOWN  # add this import

class MotorController:
    def __init__(self, port=ARDUINO_PORT, baud=BAUD_RATE):
        self.arduino = serial.Serial(port, baud, timeout=1)
        time.sleep(2)
        print(f"[MotorController] Connected on {port}")
        self._t0 = time.time(); self._n = 0
        self._last_fire = 0  # add

    def move(self, pan, tilt):
        cmd = f"move:{pan},{tilt}\n".encode()
        self.arduino.write(cmd)
        self._n += 1
        if (time.time() - self._t0) >= 1.0:
            print(f"[RATE] cmds/s={self._n} last=({pan},{tilt})")
            self._t0 = time.time(); self._n = 0

    def fire(self):  # add
        now = time.time()
        if now - self._last_fire >= SHOT_COOLDOWN:
            self.arduino.write(b"FIRE\n")
            self.arduino.flush()
            self._last_fire = now
            print("[MotorController] Blaster fired")
