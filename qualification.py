import RobotAPI as Rapi
import cv2
import numpy as np
import serial
import time

# initializing constants for hsv
BLACK_UP = np.array([100, 255, 78])  # for walls
BLACK_LOW = np.array([30, 37, 0])
ORANGE_UP = np.array([30, 145, 195])  # for orange lines
ORANGE_LOW = np.array([10, 30, 150])
BLUE_UP = np.array([120, 205, 185])  # for blue lines
BLUE_LOW = np.array([88, 70, 50])

DRAW = True  # initializing constants for drawing the borders on the image

# initializing constants for coordinates of areas in the image
X1_1_PD = 615  # for walls
X2_1_PD = 640
X1_2_PD = 0
X2_2_PD = 25
Y1_PD = 290
Y2_PD = 480

X1_LINE = 300  # for counting lines
X2_LINE = 380
Y1_LINE = 420
Y2_LINE = 480

X1_CUB = 30  # for sings detection
X2_CUB = 610
Y1_CUB = 210
Y2_CUB = 440

# initializing constants of ratio for controllers
KP = 0.013  # the proportional gain, a tuning parameter for walls
KD = 0.05  # the derivative gain, a tuning parameter for walls


class Frames:  # clsss for areas on the picture
    def __init__(self, img, x_1, x_2, y_1, y_2, low, up):  # init gains coordinates of the area, and hsv boders
        self.x_1 = x_1  # initializing variables in class
        self.x_2 = x_2
        self.y_1 = y_1
        self.y_2 = y_2
        self.up = up
        self.low = low

        self.contours = 0
        self.frame = 0
        self.hsv = 0
        self.mask = 0
        self.frame_gaussed = 0

        self.update(img)

    def update(self, img):  # function for updating the image
        # getting the needed area on the image and outlining it
        cv2.rectangle(img, (self.x_1, self.y_1), (self.x_2, self.y_2), (150, 0, 50), 2)

        self.frame = img[self.y_1:self.y_2, self.x_1:self.x_2]
        self.frame_gaussed = cv2.GaussianBlur(self.frame, (1, 1), cv2.BORDER_DEFAULT)  # blurring the image

        self.hsv = cv2.cvtColor(self.frame_gaussed, cv2.COLOR_BGR2HSV)  # turning the image from bgr to hsv

    def find_contours(self, n=0, to_draw=True, color=(0, 0, 255), min_area=50):  # function for selecting
        # the contours, it gets, the needed borders of hsv, if the borders should be drawn, color of the outlining,
        # minimum area of the contour
        self.mask = cv2.inRange(self.hsv, self.low[n], self.up[n])  # getting the mask

        _, contours, hierarchy = cv2.findContours(self.mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # getting contours
        r_contours = []
        for i in contours:  # outlining and selecting only big enough contours
            if cv2.contourArea(i) > min_area:
                r_contours.append(i)
                if to_draw:
                    cv2.drawContours(self.frame, i, -1, color, 2)

        return r_contours  # returning contours


def pd():  # function of proportional–derivative controller for walls
    global pd_1, pd_2, KD, KP, e_old, timer_flag, time_turn, tim
    global flag_left, flag_right, time_green, time_red, u  # needed global variables for this function

    u_plus = 0  # getting the addition to pd, to compensate the angle of the camera
    if direction == 'wise':
        u_plus = -10
    if direction == 'counter wise':
        u_plus = -15

    contours = pd_1.find_contours(to_draw=DRAW, color=(255, 255, 0))  # getting the contours for 1_st area
    area_1 = map(cv2.contourArea, contours)  # getting the area of the biggest contour
    if contours:
        area_1 = max(area_1)
    else:
        area_1 = 0

    contours = pd_2.find_contours(to_draw=DRAW, color=(255, 255, 0))  # same for 2_nd area
    area_2 = map(cv2.contourArea, contours)
    if contours:
        area_2 = max(area_2)
    else:
        area_2 = 0

    e = area_2 - area_1  # counting the error and the final value of pd
    u = e * KP + ((e - e_old) // 10) * KD + 128 + u_plus
    e_old = e

    if u > 160:  # limiting the turning of servo
        u = 160

    if area_2 != 0 and area_1 == 0:  # if there is no wall in one of ares, turning to the max to needed side
        flag_right = True  # changing the flag or turning
        if not timer_flag:  # resetting the timer of turning
            if time.time() - time_green < 0.2:  # if the turn, right after the inner sing, turn to the max
                if direction == 'wise':
                    time_turn = time.time() - 5
            else:
                time_turn = time.time()
            timer_flag = True

        if time.time() - time_turn > 0.1:
            u = 160

        else:
            u = 140

    elif area_1 != 0 and area_2 == 0:  # same as the previous
        flag_left = True
        if not timer_flag:
            if time.time() - time_red < 0.2:
                if direction == 'counter wise':
                    time_turn = time.time() - 5
            else:
                time_turn = time.time()

            timer_flag = True

        if time.time() - time_turn > 0.1:
            u = 60
        else:
            u = 100

    elif area_1 == 0 and area_2 == 0:  # if there's no wall in any area, turn to the same side as before
        if flag_right:
            if time.time() - time_turn > 0.1:
                u = 160
            else:
                u = 140

        elif flag_left:
            if time.time() - time_turn > 0.1:
                u = 60
            else:
                u = 100

    else:  # else resetting the flags
        flag_left = False
        flag_right = False
        timer_flag = False

    if u < 60:  # limiting the max turning for servo
        u = 60
    return int(u)  # returning controlling influence of pd


def restart():  # function for resetting all the variables
    global orange, blue, u, e_old, tim, time_orange, time_blue, stop_flag, time_turn, time_speed, speed_def
    global pause_flag, flag_line_blue, flag_line_orange, direction, time_stop, flag_left, flag_right, timer_flag

    orange = 0
    blue = 0

    timer_flag = False

    speed_def = 35

    u = 125
    e_old = 0

    tim = time.time()
    time_orange = time.time() - 5
    time_blue = time.time() - 5
    time_turn = time.time() - 5
    time_speed = time.time() + 200
    time_stop = time.time()

    stop_flag = False
    pause_flag = False
    flag_left = False
    flag_right = False
    flag_line_orange = False
    flag_line_blue = False

    direction = ''


ser = serial.Serial(
    port='/dev/ttyS0',  # Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
    baudrate=115200,
    stopbits=serial.STOPBITS_ONE
)

ser.flushInput()
ser.flushOutput()

if not ser.isOpen():
    ser.open()
    print(1)

orange = 0  # variables, for counting lines
blue = 0

u = 125  # variables for pd
e_old = 0
speed_def = 35

# initializing timers
tim = time.time()  # for finish
time_orange = time.time() - 5  # for counting orange lines
time_blue = time.time() - 5  # for counting blue lines
time_turn = time.time() - 5  # for turns
time_speed = time.time() + 200  # for slowing down at the start(optional)
time_stop = time.time()  # for stopping the robot

# initializing flags
timer_flag = False  # for resetting other variables only once
stop_flag = False  # for stopping the robot
pause_flag = False  # for pausing the robot
flag_left = False  # for tracking turns to the left
flag_right = False  # for tracking turns to the right
flag_line_orange = False  # for tracking orange lines
flag_line_blue = False  # for tracking blue lines

direction = ''  # direction variable

print(1)

robot = Rapi.RobotAPI(flag_serial=False)  # initializing object needed to manage the camera
robot.set_camera(100, 640, 480)  # setting up the camera
frame = robot.get_frame(wait_new_frame=1)

# initializing objects for different areas
pd_1 = Frames(frame, X1_1_PD, X2_1_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP])  # for the right wall
pd_2 = Frames(frame, X1_2_PD, X2_2_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP])  # for the left wall
line = Frames(frame, X1_LINE, X2_LINE, Y1_LINE, Y2_LINE, [BLUE_LOW, ORANGE_LOW], [BLUE_UP, ORANGE_UP])  # for counting
# lines

robot.set_frame(frame, 40)

# variables for counting fps
time_fps = time.time()
fps = 0
fps_last = 0

while True:  # main loop
    if time.time() - time_speed > 3:  # checking of the speed raising
        speed_def = 35
    # resetting controlling influence and speed
    u = -1
    speed = speed_def
    fps += 1
    frame = robot.get_frame(wait_new_frame=1)  # getting image from camera

    # if there is no sings, the robot will drive between walls
    pd_1.update(frame)  # updating wall areas
    pd_2.update(frame)
    u = pd()  # counting controlling influence

    line.update(frame)  # updating line-counting area
    contours_blue = line.find_contours(0, DRAW, min_area=500)  # getting bue and orange areas
    contours_orange = line.find_contours(1, DRAW, min_area=500, color=(255, 255, 0))

    if contours_blue:  # if there is blue contour, checking, if the line is new, and adding it
        contours_blue = max(contours_blue, key=cv2.contourArea)
        ar = cv2.contourArea(contours_blue)
        if ar > 10:
            if not flag_line_blue and time.time() - time_blue > 1:
                if not direction:
                    direction = 'counter wise'
                blue += 1
                if blue == 1 and orange == 0:
                    time_speed = time.time()
                print('orange: ' + str(orange) + '\n blue: ' + str(blue))
                time_blue = time.time()  # resetting timer for blue lines
                tim = time.time()  # resetting timer for stopping
            flag_line_blue = True
    else:
        flag_line_blue = False

    if contours_orange:  # same as for blue line
        contours_orange = max(contours_orange, key=cv2.contourArea)
        ar = cv2.contourArea(contours_orange)
        if ar > 10:
            if not flag_line_orange and time.time() - time_orange > 1:
                if not direction:
                    direction = 'wise'
                orange += 1
                if orange == 1 and blue == 0:
                    time_speed = time.time()
                time_orange = time.time()
                print('orange: ' + str(orange) + '\n blue: ' + str(blue))
                tim = time.time()
            flag_line_orange = True
    else:
        flag_line_orange = False

    if (max(orange, blue) > 11 and time.time() - tim > 1.2) or stop_flag:  # checking if the robot must stop
        if not stop_flag:
            time_stop = time.time()
        if time.time() - time_stop < 0.3:  # braking for 0.3 seconds
            speed = -50
            u = 127
        else:  # stopping the robot
            u = 127
            speed = 0
        mesg = str(u + 100) + str(speed + 200) + '$'  # forming the message for pyboard
        ser.write(mesg.encode('utf-8'))  # sending message to pyboard
        stop_flag = True

    if pause_flag:  # checking if the robot is paused
        u = 127
        speed = 0

    if not stop_flag:  # checking if robot is not stopped/breaking
        frame = cv2.putText(frame, ' '.join([str(speed), str(u), str(fps_last)]), (20, 30),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # printing parameters on the image
        mesg = str(u + 100) + str(speed + 200) + '$'  # sending message to pyboard
        ser.write(mesg.encode('utf-8'))  # sending message to pyboard

    if time.time() - time_fps > 1:  # counting fps
        time_fps = time.time()
        fps_last = fps
        fps = 0

    robot.set_frame(frame, 40)  # sending changed image

    key = robot.get_key()  # getting clicked button
    if key != -1:
        if key == 83:  # if s is clicked, pausing the robot
            pause_flag = True
        elif key == 71:  # if g is clicked unpausing the robot
            pause_flag = False
        elif key == 82:  # if r is clicked restarting the robot
            restart()
