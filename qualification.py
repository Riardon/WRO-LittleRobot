import RobotAPI as Rapi
import cv2
import numpy as np
import serial
import time

# создание констант для границ hsv
BLACK_UP = np.array([90, 255, 75])  # для стенок
BLACK_LOW = np.array([0, 40, 0])
ORANGE_UP = np.array([50, 185, 235])  # для ораньжевых линий
ORANGE_LOW = np.array([10, 40, 110])
BLUE_UP = np.array([140, 215, 225])  # для синих линий
BLUE_LOW = np.array([90, 70, 70])

DRAW = True  # коснтанта обозначающая, нужно ли рисовать контуры на изображении

# создание констант координат выделяемых зон на изображении
X1_1_PD = 615  # для стенок
X2_1_PD = 640
X1_2_PD = 0
X2_2_PD = 25
Y1_PD = 280
Y2_PD = 480

X1_LINE = 300  # для подсчёта линий
X2_LINE = 380
Y1_LINE = 420
Y2_LINE = 480

# создание констант коэффициентов для регуляторов
KP = 0.013  # пропорциональная составляющая для езды по стенкам
KD = 0.05  # дифференцирующая составляющая для езды по стенкам\


class Frames:  # класс для зон выделяемых на картинке
    def __init__(self, img, x_1, x_2, y_1, y_2, low, up):  # в ините указывается координаты и список границ для hsv
        self.x_1 = x_1  # создание переменных в классе
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

    def update(self, img):  # функция обновления изображения
        # выделение вырезанной зоны на основном изображении
        cv2.rectangle(img, (self.x_1, self.y_1), (self.x_2, self.y_2), (150, 0, 50), 2)

        self.frame = img[self.y_1:self.y_2, self.x_1:self.x_2]  # вырезание зоны на изображении
        self.frame_gaussed = cv2.GaussianBlur(self.frame, (1, 1), cv2.BORDER_DEFAULT)  # размытие изображения

        self.hsv = cv2.cvtColor(self.frame_gaussed, cv2.COLOR_BGR2HSV)  # перевод в цветовую модель hsv

    def find_contours(self, n=0, to_draw=True, color=(0, 0, 255), min_area=50):  # функция выделения контуров,
        # передаются необходимые границы в hsv, нужно ли отрисовывать границы на изображении, цвет отрисовки, и
        # минимальная необходимая площадь контура
        self.mask = cv2.inRange(self.hsv, self.low[n], self.up[n])  # накладываем маску на изображение

        _, contours, hierarchy = cv2.findContours(self.mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # выделяем контуры
        r_contours = []
        for i in contours:  # проходимся по контурам, оставляя и отрисовывая только достаточно большие
            if cv2.contourArea(i) > min_area:
                r_contours.append(i)
                if to_draw:
                    cv2.drawContours(self.frame, i, -1, color, 2)

        return r_contours  # возвращаем отсортированные контуры


def pd():  # функция пд для движения по стенкам
    global pd_1, pd_2, KD, KP, e_old, timer_flag, time_turn, tim
    global flag_left, flag_right, time_green, time_red, u, after_cub  # обозночение глобальных переменных, необходимых
    # в функции

    u_plus = 0  # определяем добавку к управляещему воздействию, для компенсации неровности камеры
    if direction == 'wise':
        u_plus = 0
    if direction == 'counter wise':
        u_plus = -10

    contours = pd_1.find_contours(to_draw=DRAW, color=(255, 255, 0))  # определение контуров стенки на двух зонах
    area_1 = map(cv2.contourArea, contours)  # находим площади контуров
    if contours:
        area_1 = max(area_1)
    else:
        area_1 = 0

    contours = pd_2.find_contours(to_draw=DRAW, color=(255, 255, 0))
    area_2 = map(cv2.contourArea, contours)  # находим площади контуров
    if contours:
        area_2 = max(area_2)
    else:
        area_2 = 0

    e = area_2 - area_1  # рассчёт ошибки и управляющего воздействия для пд
    u = e * KP + ((e - e_old) // 10) * KD + 128 + u_plus
    e_old = e

    if u > 160:  # ограничиваем максимальный поворот сервы
        u = 160

    if area_2 != 0 and area_1 == 0:  # если в одной из зон нет стенки, включаем максимальный поворот в нужную сторону
        flag_right = True  # включаем флаг поворота
        if not timer_flag:  # обнонуляем таймеры поворота
            time_turn = time.time()
            timer_flag = True

        if time.time() - time_turn > 0.1:
            u = 160

    elif area_1 != 0 and area_2 == 0:  # аналагично предыдущему
        flag_left = True
        if not timer_flag:
            time_turn = time.time()
            timer_flag = True

        if time.time() - time_turn > 0.1:
            u = 70

    elif area_1 == 0 and area_2 == 0:  # если нет ни на зоне нет стенки включаем поворот в туже сторону что и раньше
        # или в сорону движения линии
        if flag_right:  # если поворот был вправо поворачиваем направо
            if time.time() - time_turn > 0.1:
                u = 160

        elif flag_left:  # если поворот был влево поворачиваем налево
            if time.time() - time_turn > 0.1:
                u = 70

    else:  # обнуление флагов, если на обоих зонах есть стенка
        after_cub = False
        flag_left = False
        flag_right = False
        timer_flag = False

    if u < 70:  # ограничиваем максимальный поворот сервы
        u = 70
    return int(u)  # возвращаем управляющее воздействие


def restart():  # функция для обновления все пременных и запуска
    global orange, blue, u, e_old, tim, time_orange, time_blue, stop_flag, time_turn, time_green, time_red, time_speed
    global pause_flag, flag_line_blue, flag_line_orange, direction, time_stop, flag_left, flag_right, timer_flag

    orange = 0
    blue = 0

    timer_flag = False

    u = 125
    e_old = 0

    tim = time.time()
    time_orange = time.time()
    time_blue = time.time()
    time_turn = time.time() - 5
    time_green = time.time() - 2
    time_red = time.time() - 2
    time_speed = time.time() + 200
    time_stop = time.time()

    stop_flag = False
    pause_flag = False
    flag_left = False
    flag_right = False
    flag_line_orange = False
    flag_line_blue = False

    direction = ''



ser = serial.Serial(  # подключения uart порта
    port='/dev/ttyS0',  # Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
    baudrate=115200,
    stopbits=serial.STOPBITS_ONE
)

ser.flushInput()
ser.flushOutput()

if not ser.isOpen():
    ser.open()
    print(1)

orange = 0  # создаём переменные для подсчёта линий
blue = 0

u = 125  # создание переменных для пд
e_old = 0
speed_def = 25

# создание таймеров
tim = time.time()  # таймер для финиша
time_orange = time.time()  # таймер для подсчёта ораньжевых линий
time_blue = time.time()  # таймер для подсчёта синих линий
time_turn = time.time() - 5  # таймер для поворотов
time_speed = time.time() + 200  # таймер для замедления в начале
time_stop = time.time()  # создание таймера для торможения робота

# создание флагов
timer_flag = False  # флаг для единичного обнуления флагов
stop_flag = False  # флаг для остановки робота
pause_flag = False  # флаг для паузы робота
flag_left = False  # флаг для отслеживания поворота налево
flag_right = False  # флаг для отслеживания поворота напрвао
flag_line_orange = False  # флаг для отслеживвания ораньжевых линий
flag_line_blue = False  # флаг для отслеживвания синих линий

direction = ''  # переменная направления

print(1)

robot = Rapi.RobotAPI(flag_serial=False)  # создание обьекта класса для управления камерой
robot.set_camera(100, 640, 480)  # найстройка камеры
frame = robot.get_frame(wait_new_frame=1)

# создание обьектов классов для зон изображения
pd_1 = Frames(frame, X1_1_PD, X2_1_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP]) # для правой стенки
pd_2 = Frames(frame, X1_2_PD, X2_2_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP]) # для левой стенки
line = Frames(frame, X1_LINE, X2_LINE, Y1_LINE, Y2_LINE, [BLUE_LOW, ORANGE_LOW], [BLUE_UP, ORANGE_UP])  # для подсчёта
# линий

robot.set_frame(frame, 40)

# переменные для подсчёта fps
time_fps = time.time()
fps = 0
fps_last = 0

while True:  # основной цикл программы
    # обновление управляющего воздействия и скорости
    u = -1
    speed = 50
    fps += 1  # добавления счётчика fps
    frame = robot.get_frame(wait_new_frame=1)  # берём изображения с камеры
    pd_1.update(frame)  # обновляем обьекты стенок
    pd_2.update(frame)
    u = pd()  # формируем упраляющее воздействие

    line.update(frame)  # обновляем объект для подсчёта линий
    contours_blue = line.find_contours(0, DRAW, min_area=500)  # определяем контур синей и ораньжевой линии
    contours_orange = line.find_contours(1, DRAW, min_area=500)

    if contours_blue:  # если есть синия линия проверяем новая ли это линия и добавляем к счётчика
        contours_blue = max(contours_blue, key=cv2.contourArea)
        ar = cv2.contourArea(contours_blue)
        if ar > 10:
            if not flag_line_blue and time.time() - time_blue > 0.8:
                if not direction:
                    direction = 'counter wise'
                blue += 1
                if blue == 1 and orange == 0:
                    time_speed = time.time()
                print('orange: ' + str(orange) + '\n blue: ' + str(blue))
                time_blue = time.time()  # обновляем таймер для синих линий
                tim = time.time()  # обновляем таймер для остановки робота
            flag_line_blue = True
    else:
        flag_line_blue = False

    if contours_orange:  # аналогично синей линии
        contours_orange = max(contours_orange, key=cv2.contourArea)
        ar = cv2.contourArea(contours_orange)
        if ar > 10:
            if not flag_line_orange and time.time() - time_orange > 0.8:
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

    if (max(orange, blue) > 11 and time.time() - tim > 1.2) or stop_flag:  # проверяем нужно ли роботу останавливаться
        if not stop_flag:
            time_stop = time.time()
        if time.time() - time_stop < 0.3:  # торможение на 0.3 секунды
            speed = -50
            u = 127
        else:  # останавливаем робота
            u = 127
            speed = 0
        mesg = str(u + 100) + str(speed + 200) + '$'  # формируем сообщение для pyboard
        ser.write(mesg.encode('utf-8'))  # отправляем сообщение на pyboard
        stop_flag = True  # указываем что робот остановился/тормозит

    if pause_flag:  # проверяем на паузе ли робот
        u = 127
        speed = 0

    if not stop_flag:  # если робот не остановился/тормозит
        frame = cv2.putText(frame, ' '.join([str(speed), str(u), str(fps_last)]), (20, 30),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # выводим параметры на изображение
        mesg = str(u + 100) + str(speed + 200) + '$'  # формируем сообщение для pyboard
        ser.write(mesg.encode('utf-8'))  # отправляем сообщение на pyboard

    if time.time() - time_fps > 1:  # подсчитываем fps
        time_fps = time.time()
        fps_last = fps
        fps = 0

    robot.set_frame(frame, 40)  # отправляем изменёное изображение

    key = robot.get_key()  # забиарем нажатую на комьютере кнопку
    if key != -1:
        if key == 83:  # если нажато s ставим робота на паузу
            pause_flag = True
        elif key == 71:  # если нажато g снимаем робота с паузы
            pause_flag = False
        elif key == 82:  # если нажато r перезапускаем робота
            restart()
