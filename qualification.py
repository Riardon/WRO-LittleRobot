from bot import AdamIMU
import cv2
import numpy as np
import serial
import time


def mapp(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def pd(U):
    global pd_1_hsv, pd_1_frame, pd_2_hsv, pd_2_frame, kd, kp, e_old, stop_flag

    pd_1_mask = cv2.inRange(pd_1_hsv, np.array([0, 0, 0]), np.array([256, 256, 50]))
    contours, hierarchy = cv2.findContours(pd_1_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    area_1 = [0]
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5:
            area_1.append(area)
            cv2.drawContours(pd_1_frame, contour, -1, (0, 0, 255), 2)
    area_1 = max(area_1)

    pd_2_mask = cv2.inRange(pd_2_hsv, np.array([0, 0, 0]), np.array([256, 256, 50]))
    contours, hierarchy = cv2.findContours(pd_2_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    area_2 = [0]
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5:
            area_2.append(area)
            cv2.drawContours(pd_2_frame, contour, -1, (0, 0, 255), 2)
    area_2 = max(area_2)
    e = area_2 - area_1
    # robot.fprint(str(area_1) + ' ' + str(area_2))
    # robot.fprint(h)
    u = e * kp + (e - e_old) * kd + 90
    e_old = e
    if u > 135 or (area_1 == 0 and area_2 != 0):
        u = 135
    elif u < 60 or (area_2 == 0 and area_1 != 0):
        u = 60
    stop_flag = abs(area_1 - area_2) < 1800
    return int(u)


'''стенка 8 - 200'''
HUE_MIN = 0
HUE_MAX = 180
SAT_MIN = 0
SAT_MAX = 256
VAL_MIN = 0
VAL_MAX = 256

ser = serial.Serial(
        port='/dev/ttyAMA0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        write_timeout=0.
)

ser.flushInput()
ser.flushOutput()

if (ser.isOpen() == False):
    ser.open()
    print(1)

SPEED_DEF = 50

speed = 100

robot = AdamIMU()

robot.fprint("START FRAME ADAM", robot)
count = 0
n = 0

t = 0

count_lines = 0

u = 90
e_old = 0
e = 0
kp = 0.014
kd = 0.02
flag = 0
tim = time.time()
stop_flag = False
flag_line = 0

try:

    while True:
        stop_flag = False
        frame = robot.get_frame()
        frame = cv2.resize(frame, (640, 480))

        x1_1_pd = 590
        x2_1_pd = 640
        x1_2_pd = 0
        x2_2_pd = 50
        y1_pd = 250
        y2_pd = 480
        cv2.rectangle(frame, (x1_1_pd, y1_pd), (x2_1_pd, y2_pd), (150, 0, 50), 2)
        pd_1_frame = frame[y1_pd:y2_pd, x1_1_pd:x2_1_pd]
        pd_1_hsv = cv2.cvtColor(pd_1_frame, cv2.COLOR_BGR2HSV)
        cv2.rectangle(frame, (x1_2_pd, y1_pd), (x2_2_pd, y2_pd), (150, 0, 50), 2)
        pd_2_frame = frame[y1_pd:y2_pd, x1_2_pd:x2_2_pd]
        pd_2_hsv = cv2.cvtColor(pd_2_frame, cv2.COLOR_BGR2HSV)

        u = pd(u)

        x1_line = 300
        x2_line = 380
        y1_line = 420
        y2_line = 480
        line_frame = frame[y1_line:y2_line, x1_line:x2_line]
        line_hsv = cv2.cvtColor(line_frame, cv2.COLOR_BGR2HSV)
        line_mask = cv2.inRange(line_hsv, np.array([80, 40, 70]), np.array([140, 250, 160]))
        contours, hierarchy = cv2.findContours(line_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(line_frame, contours, -1, (0, 0, 255), 2)
        line_hsv_out = cv2.resize(line_mask, (640, 480))
        cv2.rectangle(frame, (x1_line, y1_line), (x2_line, y2_line), (255, 0, 0), 2)
        if contours:
            # robot.fprint(cv2.contourArea(contours[0]))
            contours = max(contours, key=cv2.contourArea)
            ar = cv2.contourArea(contours)
            if ar > 10:
                if flag_line == 0:
                    count_lines += 1
                    tim = time.time()
                flag_line = 1
        else:
            flag_line = 0
            robot.fprint(str(count_lines))
        if speed < 100 and count_lines > 1 and time.time() - tim > 0.7:
            speed = 100


        if count_lines > 11 and time.time() - tim > 0.6:
            if time.time() - tim > 6:
                count_lines = 0
            speed = 0

        mesg = str(u) + ' ' + str(speed) + '$'
        ser.write(mesg.encode('utf-8'))

        robot.set_frame(frame, 40)

        n = n % 1000

except Exception as er:
    while 1:
        robot.fprint(er)