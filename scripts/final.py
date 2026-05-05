import ikpy.chain
import numpy as np
import os
import sys
import termios
import tty
import time
from python_st3215 import ST3215
import json

# Load the config we just generated
try:
    with open('arm_config.json', 'r') as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    print("Config not found! Run calibrate_arm.py first.")
    sys.exit()

# --- 1. CONFIGURATION ---
PORT = "/dev/ttyACM0"
BAUD = 1000000
URDF_PATH = os.path.join(os.path.dirname(__file__), "../models/so101_arm.urdf")

# STS3125 Register Map (Standard Feetech Protocol)
INST_WRITE = 0x03
REG_TORQUE_ENABLE = 0x28  # 1 byte
REG_GOAL_POSITION = 0x2A  # 2 bytes (Low, High)
REG_GOAL_SPEED    = 0x2E  # 2 bytes (Low, High)

# --- 2. INITIALIZE HARDWARE & IK ---
bus = ST3215(PORT, baudrate=BAUD)
my_chain = ikpy.chain.Chain.from_urdf_file(
    URDF_PATH, 
    active_links_mask=[False, True, True, True, True, True, True]
)

current_pos = [0.15, 0.0, 0.15]
last_angles = np.zeros(len(my_chain.links)) 

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def rad_to_sts_steps(radians, servo_id):
    # Convert ID to string for JSON lookup
    sid = str(servo_id)
    center = CONFIG['centers'].get(sid, 2000)
    
    steps = int(center + (radians * (4096 / (2 * np.pi))))
    
    # Safety limits
    mini = CONFIG['min_limits'].get(sid, 0)
    maxi = CONFIG['max_limits'].get(sid, 4095)
    
    # Ensure mini is actually the smaller value
    low, high = sorted([mini, maxi])
    return max(low, min(high, steps))

# In your move_servos loop, pass the ID:
# steps = rad_to_sts_steps(rad, servo_id)

def write_register(servo_id, reg, values):
    """Helper to send raw data to specific registers."""
    if not isinstance(values, list):
        values = [values]
    bus.send_instruction(servo_id, INST_WRITE, [reg] + values)

def move_servos(angles):
    """Sends position commands to all 6 servos."""
    for i, rad in enumerate(angles[1:7]):
        servo_id = i + 1
        steps = rad_to_sts_steps(rad,servo_id)
        
        # Split 16-bit position into 2 bytes (Little Endian)
        low = steps & 0xFF
        high = (steps >> 8) & 0xFF
        write_register(servo_id, REG_GOAL_POSITION, [low, high])

def update_display(angles):
    os.system('clear')
    print("--- SO101 REAL-TIME CONTROL ---")
    print(f"Target XYZ: {np.round(current_pos, 3)}")
    print("-" * 35)
    print("Servo Positions (Steps):")
    for i, rad in enumerate(angles[1:7]):
        servo_id = i + 1
        print(f"  ID {i+1}: {rad_to_sts_steps(rad,servo_id)}")
    print("-" * 35)
    print("w/s: X | a/d: Y | r/f: Z | q: QUIT")

# --- 3. WAKE UP SERVOS ---
print("Waking up servos and enabling torque...")
for i in range(1, 7):
    # Enable Torque
    write_register(i, REG_TORQUE_ENABLE, 0x01)
    # Set Speed (e.g., 800)
    speed = 800
    write_register(i, REG_GOAL_SPEED, [speed & 0xFF, (speed >> 8) & 0xFF])
    time.sleep(0.05)

# Initial move to starting coordinate
last_angles = my_chain.inverse_kinematics(current_pos, initial_position=last_angles)
move_servos(last_angles)
update_display(last_angles)

# --- 4. MAIN LOOP ---
try:
    while True:
        char = getch().lower()
        step = 0.01 
        
        if char == 'w': current_pos[0] += step
        elif char == 's': current_pos[0] -= step
        elif char == 'a': current_pos[1] += step
        elif char == 'd': current_pos[1] -= step
        elif char == 'r': current_pos[2] += step
        elif char == 'f': current_pos[2] -= step
        elif char == 'q': 
            break

        # Calculate IK
        last_angles = my_chain.inverse_kinematics(current_pos, initial_position=last_angles)
        
        # Move Hardware
        move_servos(last_angles)
        
        # Update UI
        update_display(last_angles)

except KeyboardInterrupt:
    pass

finally:
    print("\nDisabling Torque and Exiting...")
    for i in range(1, 7):
        write_register(i, REG_TORQUE_ENABLE, 0x00)
    bus.close()
