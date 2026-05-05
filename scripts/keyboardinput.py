import ikpy.chain
import numpy as np
import os
import sys
import termios
import tty

# --- SETUP ---
URDF_PATH = os.path.join(os.path.dirname(__file__), "../models/so101_arm.urdf")
# Load chain and ignore the fixed link warnings by defining active links# Total 7 links: 1st is fixed (False), next 6 are your servos (True)
my_chain = ikpy.chain.Chain.from_urdf_file(
    URDF_PATH, 
    active_links_mask=[False, True, True, True, True, True, True]
)
current_pos = [0.15, 0.0, 0.15]
# Initialize with zeros for all links in the chain
last_angles = np.zeros(len(my_chain.links)) 

def getch():
    """Reads a single character from terminal without waiting for Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def update_display(angles):
    os.system('clear')
    print("--- SO101 ROBOT CONTROL ---")
    print(f"Target XYZ: {np.round(current_pos, 3)}")
    print("-" * 30)
    print("Joint Angles (Radians):")
    # Indices 1 through 6 are your STS servos
    for i, a in enumerate(angles[1:7]):
        print(f"  Servo {i+1}: {a:.4f}")
    print("-" * 30)
    print("w/s: X | a/d: Y | r/f: Z | q: QUIT")

print("Controller Started. Use keys to move...")

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
        print("\nExiting...")
        break

    # Replaced 'initial_guess' with the correct 'initial_position'
    last_angles = my_chain.inverse_kinematics(current_pos, initial_position=last_angles)
    update_display(last_angles)
