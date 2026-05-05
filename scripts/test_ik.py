import ikpy.chain
import os

# Get the path to your URDF
urdf_path = os.path.join(os.path.dirname(__file__), "../models/so101_arm.urdf")

# Load the chain
my_chain = ikpy.chain.Chain.from_urdf_file(urdf_path)

# Test a target position (x, y, z in meters)
target_pos = [0.1, 0.0, 0.2] 
ik_results = my_chain.inverse_kinematics(target_pos)

print("IK Success!")
print("Computed Joint Angles:", ik_results)
