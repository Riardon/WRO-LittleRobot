# File description

On our robot we have 2 files that work at the same time. File main.py is launched on pyboard, it get's the data from raspberry and controls servo drive and motor. osnov.py(for final attempts) or kwala.py(for qualification) is launched on raspberry, it receives the image from camera, processes it, and sends data to pyboard.
RobotAPI.py - library, that is used on raspberry to help get an image from camera and display it while dubugging.
autostart.py - file on raspberry, for auto launching of the program after turning on.
module.py - library on pyboard. It's used to help controling servo and motor.

# Main.py

main.py is a program on pyboard. First of all, it waits  for a button to be pressed, than it gets the speed, and an angle for servo drive. Than it passes the speed directly to motor. And uses a proportional-derivative controller(https://en.wikipedia.org/wiki/PID_controller) to regulate the speed of the servo and set to the needed angle. 

# kwala.py

kwala.py is a program on raspberry. After it gets the image from camera, it cuts out 3 areas on it, 1 on the right side, 1 on the left, and at the bottom. The program converts them from the bgr color model to hsv, and findes the needed items on it. The ones on the left and right are used to detect the walls. After detection it uses the proportional-derivative controller to help robot move in the center between 2 walls. Then if we see 1 wall, and don't see the other, the robot starts to to turn. The part at the bottom is used to count lines, that we have passed. When the robot passes 12 lines, it stops.

# osnov.py
osnov.py is a  program on raspberry. It's practically similar to kwala.py. It's 1 more area in it, that is used to detect signes, and, based on theres position, make robot go arond them. A proportional-derivative controller is also used here.

