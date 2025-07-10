# Library Assistant System

## Project Overview
This is a complete Library Assistant System, which includes an upper-computer GUI application, a lower-computer embedded control program, and a serial communication module. It enables book location querying and automatic navigation.

## System Workflow:
1. Users query book locations through the GUI.
2. The system parses the book's area (A-F).
3. Navigation instructions are sent to the lower-computer via serial communication.
4. The lower-computer controls the vehicle to move to the specified area.

## Features

### Upper-Computer Features
- Book location querying and display.
- User-friendly graphical interface.
- Real-time interactive dialogue.
- Adjustable font size.
- Quick access to hot topics.
- Generation and sending of navigation instructions.

### Lower-Computer Features
- Precise control of four motors using PID.
- Encoder speed feedback.
- Forward/reverse PWM control.
- Motor auto-calibration.
- Speed synchronization algorithm.

### Communication Features
- Hexadecimal instruction transmission.
- Error detection and handling.
- Response reception and parsing.

## File Structure
Library-Assistant/  
├── library_core.py # Core logic: Book data processing and API interaction  
├── library_gui.py # Tkinter graphical user interface  
├── main.py # Program entry point  
├── serial_communicator.py # Serial communication module  
├── pwm_test.c # Lower-computer motor control program  
└── pwm_test.h # Lower-computer header file  

## Hardware Requirements

### Upper-Computer:
- Python 3.7+ version
- Computer with serial communication support

### Lower-Computer:
- STM32F4 series development board
- 4 DC motors with encoders
- Motor drive module
- USB to TTL serial module

## Installation and Usage

### Upper-Computer Installation
```bash
pip install tkinter
pip install pyserial
python main.py
