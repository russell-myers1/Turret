---
layout: default
title: AI-Powered Robotic Turret
---

# AI-Powered Robotic Turret

<img src="https://img.youtube.com/vi/XWiej0elrc0/maxresdefault.jpg" alt="Turret Demo Banner" width="100%" style="border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.3);margin:20px 0;" />

## Demo Video
[![AI-Powered Robotic Turret Demo](https://img.youtube.com/vi/XWiej0elrc0/0.jpg)](https://www.youtube.com/watch?v=XWiej0elrc0)

*AI-powered robotic turret powered by Raspberry Pi 5, Hailo-8L AI accelerator, and Arduino stepper control.*

---

## Overview
An AI-powered robotic turret that combines **computer vision, radar sensing, and embedded motor control**.  
The system tracks moving targets in real time and activates a gel blaster actuator when conditions are met.  

This project demonstrates **end-to-end engineering**: electronics design, embedded programming, computer vision, and full-stack integration.

---

## Features
- Real-time object detection using **Raspberry Pi 5 + Hailo-8L AI accelerator (YOLOv8)**  
- Smooth **pan/tilt motion control** with NEMA stepper motors + TB6600 drivers  
- **Arduino-controlled MOSFET trigger system** for gel blaster actuator  
- **mmWave radar (HLK-LD2450)** for coarse detection and rapid targeting  
- Modular **Python + Arduino software stack** (vision, tracking, motor, serial comms)  
- Safe power distribution with **24 V Mean Well PSU, buck converters, fusing, and emergency stop**  

---

## Software
- **Python (Raspberry Pi)**  
  - Picamera2 + OpenCV for camera input  
  - HailoRT for AI inference (.hef compiled models)  
  - Serial communication with Arduino controllers  
- **Arduino (Uno + Nano)**  
  - Uno: stepper motion + MOSFET blaster control  
  - Nano: HLK-LD2450 mmWave radar parsing and serial forwarding  

---

## Hardware
- Raspberry Pi 5 + Hailo-8L AI Accelerator  
- Raspberry Pi HQ Camera + Arducam adapter  
- 2 × NEMA stepper motors (pan/tilt) with planetary gearboxes  
- TB6600 motor drivers (microstepping at 800 pulses/rev)  
- GT2 pulleys + timing belts (e.g., 132 mm loop)  
- HLK-LD2450 mmWave radar  
- Gel blaster actuator controlled via Arduino MOSFET driver  
- Mean Well 24 V PSU + Pololu 5 V buck converter  
- Safety: inline fuses, DC breaker, push-button e-stop  

---

## System Flow
```mermaid
flowchart LR
  Radar[mmWave Radar] --> Pi[Pi 5 + Hailo-8L AI]
  Camera[Pi HQ Camera] --> Pi
  Pi -->|Serial| Uno[Arduino Uno]
  Pi -->|Serial| Nano[Arduino Nano]
  Uno --> Motors[Pan/Tilt Motors]
  Uno --> Blaster[Gel Blaster MOSFET]
