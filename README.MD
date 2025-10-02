## RUN SYSTEM
cd ~/Desktop/Turret
source venv/bin/activate
python main.py

# 🛡️ AI-Powered Robotic Turret

### Demo Video
[![AI-Powered Robotic Turret Demo](https://img.youtube.com/vi/XWiej0elrc0/0.jpg)](https://youtube.com/shorts/XWiej0elrc0)

> Click the image to watch the turret in action (Raspberry Pi 5 + Hailo-8L + Arduino).

---

## Overview
This project is a Raspberry Pi + Arduino powered robotic turret that combines **computer vision, AI acceleration, stepper motor control, and mmWave radar** for real-time tracking and firing.

- Real-time detection (YOLOv8 on Hailo-8L)  
- Smooth pan/tilt motion (NEMA steppers + TB6600 drivers)  
- Arduino MOSFET trigger control for blaster  
- mmWave radar (HLK-LD2450) for coarse snap-to-target  
- Modular Python + Arduino codebase  
