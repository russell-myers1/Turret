#hardware/blaster.py
import serial
import time
from config import BLASTER_PORT, BAUD_RATE, SHOT_COOLDOWN

class Blaster:
    def __init__(self, port=BLASTER_PORT, baud=BAUD_RATE):
        # Commented out because you had it commented in your script
        self.blaster = serial.Serial(port, baud, timeout=1)
        self.last_shot_time = 0

    def fire(self):
        if self.blaster and time.time() - self.last_shot_time > SHOT_COOLDOWN:
            self.blaster.write(b"FIRE\n")
            self.blaster.flush()
            self.last_shot_time = time.time()
            print("Blaster fired")
        pass