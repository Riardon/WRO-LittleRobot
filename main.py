from pyb import delay, Pin, ADC
from machine import UART
from module import Motor_shild, mapp
import pyb


def pd(need_deg):  # пд для серво мотора
    global serv_deg, serv, kp, kd, e_old, e  # добавление глобальных переменных, нужных в функции
    deg_now = mapp(serv_deg.read(), 0, 4095, 0, 180)  # вычилсяем нынешний угол поворота сервы
    e = - (need_deg - deg_now)  # рассчитываем ошибку
    u = e * kp + kd * (e - e_old)  # рассчитываем управляющее воздействие
    if -15 < u < 0:  # ограничиваем максимальное управляющее воздействие
        u = -15
    if 0 < u < 15:
        u = 15
    if abs(e) < 5:
        u = 0
    serv.MotorMove('A', u)


led = pyb.LED(3)  # подключение жёлтого светодиода
led.on()  # включаем светодиод
uart = UART(6, 115200, stop=1)  # подключение uart
serv_deg = ADC('X1')  # подключаем потонциометр в серве
serv = Motor_shild(('Y5', 'Y6', 'X11', 'X12'), PWM_A='Y7', PWM_B='X10')  # подключаем серву и мотор

# создаём переменные, необходимые для пд
e = 0
kp = 2
kd = 20
e_old = 0

# создаём переменные отвечающие за скорость и угол поворота
deg = 109
speed = 0

button = Pin('X6', Pin.IN, Pin.PULL_UP)  # подключаем кнопку
flag = False  # создаём флаг для отслеживания нажатия кнопки
flag_led = True  # создаём флаг для отслеживания включения светодиода
blue_led = pyb.LED(4)  # подключаем синий светодиод

inn = ''  # создаём переменную для принятия сообщения с raspberry

print(1)
while True:  # основной цикл
    if flag:  # проверяем была ли нажата кнопка
        if uart.any():  # проверяем пришли ли данные с raspberry
            a = chr(uart.readchar())  # считываем 1 знак из пришедших
            if a != '$':  # собираем сообщение до знака $
                inn += a
            else:
                try:
                    if len(inn) == 6:  # проверяем верность сообщения
                        print(inn)
                        deg, speed = int(inn[:3]) - 100, int(inn[3:]) - 200  # расшифровываем сообщение
                        # print(deg, speed)
                    inn = ''
                except ValueError:
                    print('err')
        pd(deg)  # запускаем пд на серво моторе
        serv.MotorMove('B', speed)  # запускаем мотор на нужной скорости
    else:
        if flag_led:  # включаем синий светодиод, если данные с raspberry начали приходить
            if uart.any():
                flag_led = False
                blue_led.on()

    ort = button.value()  # считываем данные нажатия кнопки

    if ort == 0:
        serv.MotorMove('A', 0)  # если кнопка нажата стопим серву и мотор
        serv.MotorMove('B', 0)
        delay(50)
        while button.value() == 0:  # ждём отжатия кнопки
            pass
        flag = not flag  # меняем флаг нажатия кнопки
        print('pressed')
        delay(50)

