# hardware/motor_controller.py
import serial, time
from config import ARDUINO_PORT, BAUD_RATE

class MotorController:
    def __init__(self, port=ARDUINO_PORT, baud=BAUD_RATE):
        self.arduino = serial.Serial(port, baud, timeout=1)
        time.sleep(2)
        print(f"[MotorController] Connected on {port}")
        self._last = (None, None)
        self._t0 = time.time(); self._n = 0

    def move(self, pan, tilt):
        cmd = f"move:{pan},{tilt}\n".encode()
        self.arduino.write(cmd)
        # Debug: command rate / changes (remove after testing)
        self._n += 1
        if (time.time() - self._t0) >= 1.0:
            print(f"[RATE] cmds/s={self._n} last=({pan},{tilt})")
            self._t0 = time.time(); self._n = 0
