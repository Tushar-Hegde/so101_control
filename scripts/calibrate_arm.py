import time
import json
import serial # We use the raw serial library to avoid the ST3215 bugs
from python_st3215 import ST3215

# --- CONFIG ---
PORT = "/dev/ttyACM0"
BAUD = 1000000

# Standard STS Protocol bytes
# Packet: [0xFF, 0xFF, ID, Length, Instruction, Param1, Param2, Checksum]
def get_pos_manual(ser, servo_id):
    # Instruction 0x02 (READ), Register 0x38 (Position), Length 0x02
    checksum = ~(servo_id + 0x04 + 0x02 + 0x38 + 0x02) & 0xFF
    packet = bytes([0xFF, 0xFF, servo_id, 0x04, 0x02, 0x38, 0x02, checksum])
    
    ser.write(packet)
    time.sleep(0.02)
    
    if ser.in_waiting >= 8:
        response = ser.read(ser.in_waiting)
        # Find the header 0xFF, 0xFF in the response
        for i in range(len(response) - 7):
            if response[i] == 0xFF and response[i+1] == 0xFF and response[i+2] == servo_id:
                # Position is at index i+5 (Low) and i+6 (High)
                low = response[i+5]
                high = response[i+6]
                return low + (high << 8)
    return None

def main():
    # We open our own serial connection to bypass the library's broken methods
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    config = {'centers': {}, 'max_limits': {}, 'min_limits': {}}
    
    print("--- SO101 PROTOCOL-LEVEL CALIBRATOR ---")
    print("Torque is OFF. Move the arm manually.")

    steps = [
        ("centers", "Move arm to 'HOME' pose (0 radians in URDF)."),
        ("max_limits", "Move arm to its MAXIMUM safe rotation."),
        ("min_limits", "Move arm to its MINIMUM safe rotation.")
    ]

    for key, message in steps:
        print(f"\nSTEP: {message}")
        input("Press Enter to capture...")
        for i in range(1, 7):
            pos = get_pos_manual(ser, i)
            if pos is not None:
                config[key][i] = pos
                print(f"  ID {i}: {pos}")
            else:
                print(f"  ID {i}: READ FAILED")
                config[key][i] = 2000 if key == "centers" else (4095 if key == "max_limits" else 0)

    ser.close()

    # Save to JSON
    with open('arm_config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n" + "="*35)
    print("SUCCESS: 'arm_config.json' saved.")
    print("="*35)

if __name__ == "__main__":
    main()
