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
BLUE_UP_CHECK_DIR = np.array([130, 215, 115])  # для синих линий, для определения направления
BLUE_LOW_CHECK_DIR = np.array([70, 70, 70])
ORANGE_UP_CHECK_DIR = np.array([50, 185, 175])  # для ораньжевых линий, для определения направления
ORANGE_LOW_CHECK_DIR = np.array([15, 80, 70])
GREEN_UP = np.array([90, 255, 130])  # для зелёных знаков
GREEN_LOW = np.array([40, 170, 60])
RED_UP = np.array([15, 205, 215])  # для красных знаков
RED_LOW = np.array([0, 80, 80])

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

X1_CUB = 30  # для детекции знаков
X2_CUB = 610
Y1_CUB = 210
Y2_CUB = 440

X1_CHECK_DIR = 260  # для опрделения направления
X2_CHECK_DIR = 380
Y1_CHECK_DIR = 320
Y2_CHECK_DIR = 340

# создание констант коэффициентов для регуляторов
KP = 0.013  # пропорциональная составляющая для езды по стенкам
KD = 0.05  # дифференцирующая составляющая для езды по стенкам
K_X = 0.05  # пропорциональная составляющая для объезда знаков
K_Y = 0.04  # дифференцирующая составляющая для объезда знаков


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
    if contours:
        area_1 = max(contours)
    else:
        area_1 = 0

    contours = pd_2.find_contours(to_draw=DRAW, color=(255, 255, 0))
    if contours:
        area_2 = max(contours)
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
            if time.time() - time_green < 0.2:  # если поворот сразу после внутреннего кубика начинаем максимальный
                # поворот сразу
                after_cub = True
                if direction == 'wise':
                    time_turn = time.time() - 5
            else:
                time_turn = time.time()
            timer_flag = True

        if time.time() - time_turn > 0.5:
            u = 160

        else:
            u = 140

    elif area_1 != 0 and area_2 == 0:  # аналагично предыдущему
        flag_left = True
        if not timer_flag:
            if time.time() - time_red < 0.2:
                after_cub = True
                if direction == 'counter wise':
                    time_turn = time.time() - 5
            else:
                time_turn = time.time()

            timer_flag = True

        if time.time() - time_turn > 0.5:
            u = 70
        else:
            u = 100

    elif area_1 == 0 and area_2 == 0:  # если нет ни на зоне нет стенки включаем поворот в туже сторону что и раньше
        # или в сорону движения линии
        if flag_right:  # если поворот был вправо поворачиваем направо
            if time.time() - time_turn > 0.5:
                u = 160
            else:
                u = 140

        elif flag_left:  # если поворот был влево поворачиваем налево
            if time.time() - time_turn > 0.5:
                u = 70
            else:
                u = 100

    else:  # обнуление флагов, если на обоих зонах есть стенка
        after_cub = False
        flag_left = False
        flag_right = False
        timer_flag = False

    if u < 70:  # ограничиваем максимальный поворот сервы
        u = 70
    return int(u)  # возвращаем управляющее воздействие


def pd_cub(color):  # функция для рассчета управляющего воздействия для объездов кубиков
    global direction, K_X, K_Y, frame, time_red, time_green, cub

    if color == 'green':  # определяем контуры знаков в зависимости от цвета знаков
        countors = cub.find_contours(to_draw=DRAW, color=(0, 255, 0), min_area=1000)
    elif color == 'red':
        countors = cub.find_contours(1, DRAW, min_area=1000)
    else:
        print('color erorr')
        return -1  # если цвет задан неправтльно, возвращаем -1 и выводим сообщение об ошибке

    if countors:
        countors = max(countors, key=cv2.contourArea)  # если контуры есть берём максимальный из них
        x, y, w, h = cv2.boundingRect(countors)  # находим крайние координаты контура
        x = (2 * x + w) // 2
        y = y + h

        if color == 'red':  # определяем координату к которой надо стремиться взависимости от цвета
            time_red = time.time()
            x_tar = 0
        elif color == 'green':
            time_green = time.time()
            x_tar = cub.x_2 - cub.x_1
        else:
            print('color erorr')
            return -1

        e_x = round((x_tar - x) * K_X, 3)  # рассчитываем ошибку по координате x
        e_y = round(y * K_Y, 3)  # рассчитываем ошибку по координате y
        e_cub = int(abs(e_y) + abs(e_x))  # рассчитываем общую ошибку

        if color == 'green':
            e_cub = int(e_cub * -1.5)

        if color == 'green':  # выводим ошибку на экран
            frame = cv2.putText(frame, str(e_cub), (20, 60),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        else:
            frame = cv2.putText(frame, str(e_cub), (20, 90),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        return e_cub  # возвращаем ошибку

    return -1  # если нет  знаков в зоне возвращаем -1


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
time_green = time.time() - 2  # таймер для отслеживания зелёных знаков
time_red = time.time() - 2  # таймер для отслеживания красных знаков
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
after_cub = False  # флаг для отслеживания поворота после кубиков

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
cub = Frames(frame, X1_CUB, X2_CUB, Y1_CUB, Y2_CUB, [GREEN_LOW, RED_LOW], [GREEN_UP, RED_UP])  # для детекции знаков
check_dir = Frames(frame, X1_CHECK_DIR, X2_CHECK_DIR, Y1_CHECK_DIR, Y2_CHECK_DIR,
                   [BLUE_LOW_CHECK_DIR, ORANGE_LOW_CHECK_DIR], [BLUE_UP_CHECK_DIR, ORANGE_UP_CHECK_DIR]) # для
# определения направления

robot.set_frame(frame, 40)

# переменные для подсчёта fps
time_fps = time.time()
fps = 0
fps_last = 0

while True:  # основной цикл программы
    if time.time() - time_speed > 3:  # проверка для повышения скорости
        speed_def = 35
    # обновление управляющего воздействия и скорости
    u = -1
    speed = speed_def
    fps += 1  # добавления счётчика fps
    frame = robot.get_frame(wait_new_frame=1)  # берём изображения с камеры

    cub.update(frame)  # обновление объекта для знаков
    if not direction:  # проверка знаем ли мы направления движения
        check_dir.update(frame)  # обновление объекта для направления
        dir_orange = check_dir.find_contours(n=1, to_draw=DRAW, min_area=100)  # находим контуры ораньжевого
        dir_blue = check_dir.find_contours(n=0, to_draw=DRAW, min_area=100, color=(0, 255, 255))  # находим контуры
        # синего
        if dir_blue:  # если есть синия линия направлени против часовой
            direction = 'counter wise'
            if after_cub:
                time_turn -= 5
            print(direction, after_cub)
        elif dir_orange:  # если есть синия линия направлени по часовой
            direction = 'wise'
            if after_cub:
                time_turn -= 5
            print(direction, after_cub)

    u_red = pd_cub('red')  # определяем направляющее воздействие по красным знакам
    u_green = pd_cub('green')  # определяем направляющее воздействие по красным знакам
    if u_green != -1 or u_red != -1:
        u = 125 + max(u_green, u_red, key=abs)  # если есть знаки формируем управляющее воздействие

    # если знаков нет, едем по стенкам
    else:
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
