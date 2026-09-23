
# SO101 Arm Control

This repo implements inverse kinematics using ikpy the open source SO101 arm model.
It should work for any arm model so long as the URDF and amr_config are accurate and uploaded in the right directory. (Not tested with other models yet)

## Execution Flow

### Calibration
Before attempting automated motion, calibrate the arm to establish physical boundaries and joint limits.
Run
```python3 scipts/calibrate_arm.py``` or the equivalent on your machine.
When prompted, move the arm to its home position, then maximum and then minimum safe rotation (For all degrees of freedom, including gripper).

### Keyboard Teleop
Run
```python3 scipts/keyboardinput.py``` in your terminal.
The arm will go to its home position, after which you can control it using :
w/s - forwards/backwards; a/d - left/right; r/f - up/down;
You will have to give the input through the terminal.

### Direct x,y,z coordinate control
Run
```python3 scipts/final.py``` in your terminal
The arm will go to its home position.
When prompted, you can input the x,y,z coordinates you want it to go to. 
It will try its best to go there within its work volume.

### NOTES : 
1. When you run the keyboard or direct controls, the arm moves to its home position. Make sure it is unobstructed and you are safely out of its path.
2. If commands are given to go outside the work volume, it does not reject the command. It tries it's best to go there within its constraints. If you continuosly give a command to go outside its work volume in the keyboard control, you will have to give the oppsite commands equally to bring it back to its work volume. Operating it far away from its work volume may cause jerkiness as it tries to correct and reach the specified point.


## Demos
These demos were captured in the EECE expo '26 held at IIT Dharwad, where the project won the "Best UG Project" title. \n
<img width="478" height="850" alt="WhatsAppVideo2026-09-23at16 31 54-ezgif com-optimize" src="https://github.com/user-attachments/assets/34cb8a48-e18c-42b5-8f50-8ca89dd7d2aa" /> \n
Homing to starting position \n
<img width="478" height="850" alt="ezgif com-optimize (1)" src="https://github.com/user-attachments/assets/48adeb2a-e4c4-4cc9-8ba1-76e9e87dc546" /> \n
Keyboard control \n
<img width="900" height="1600" alt="WhatsApp Image 2026-09-23 at 16 31 54" src="https://github.com/user-attachments/assets/f82eca2e-fc87-4114-9d94-c25513e64671" /> \n
<img width="1600" height="900" alt="WhatsApp Image 2026-09-23 at 16 31 55" src="https://github.com/user-attachments/assets/e112c15d-d225-4215-97ae-fa19dcccbc14" /> \n


## Contributors
[@TusharHegde](https://github.com/Tushar-Hegde)
[@SimarjeetSingh](https://github.com/simarjeet-singh-18)

