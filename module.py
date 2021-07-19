from pyb import Pin, Timer,ExtInt
import math,pyb,utime


def filtr_mas(mas):
    z = {}
    max_data = 0
    count = 0
    for i in mas:
        if i in z:
            z[i] += 1
        else:
            z[i] = 1
    for i in sorted(z):
        if z[i] > count:
            count = z[i]
            max_data = i
    return max_data


def pulseIn(pin,st):
    start = 0
    end = 0
    mas_filtr=[]
    # Create a microseconds counter.
    micros = Timer(5, prescaler=83, period=0x3fffffff)
    micros.counter(0)
    if st:
        while pin.value() == 0:
            start = micros.counter()

        while pin.value() == 1:
            end = micros.counter()
    else:
        while pin.value() == 1:
            start = micros.counter()

        while pin.value() == 0:
            end = micros.counter()


    micros.deinit()
    res=(end - start)
    mas_filtr=[res for i in range(10)]

    return filtr_mas(mas_filtr)


def constrain(x, out_min, out_max):
    if x < out_min:
        return out_min
    elif out_max < x:
        return out_max
    else:
        return x


def mapp(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def sum_set(x, n):
    for i in range(n):
        x += x
        return x


def interval(val, a, b, st=False):
    if not st:
        if val < a:
            return False
        elif val > b:
            return False
        else:
            return True
    if st:
        if val < a:
            return True
        elif val > b:
            return True
        else:
            return False

class PWM:
    def __init__(self,pin_i,freq=1000):

        timer_n=0
        channel=0
        self.state=False
        self.pulse_width_get=6000
        self.pulse_width=30000
        self.pin=Pin(pin_i)

        if pin_i=='A0'or pin_i=='X1':
            self.state = False
            timer_n=2
            channel=1
        elif pin_i=='A1'or pin_i=='X2':
            self.state = False
            timer_n = 2
            channel = 2
        elif pin_i=='A2'or pin_i=='X3':
            self.state = False
            timer_n = 2
            channel = 3
        elif pin_i=='A5'or pin_i=='X6':
            self.state=True
            timer_n = 8
            channel = 1

        elif pin_i == 'A6' or pin_i == 'X7':
            self.state = False
            timer_n = 13
            channel = 1

        elif pin_i=='A7'or pin_i=='X8':
            self.state = False
            timer_n = 14
            channel = 1
        elif pin_i=='B6'or pin_i=='X9':
            self.state = False
            timer_n = 4
            channel = 1
        elif pin_i=='B7'or pin_i=='X10':
            self.state = False
            timer_n = 4
            channel = 2
        elif pin_i=='B10'or pin_i=='Y9':
            self.state = False
            timer_n = 2
            channel = 3
        elif pin_i=='B11'or pin_i=='Y10':
            self.state = False
            timer_n = 2
            channel = 4
        elif pin_i=='B0'or pin_i=='Y11':
            self.state = True
            timer_n = 8
            channel = 2

        elif pin_i=='B1'or pin_i=='Y12':
            self.state = True
            timer_n = 8
            channel = 3

        elif pin_i=='B8'or pin_i=='Y3':
            self.state = False
            timer_n = 4
            channel = 3

        elif pin_i=='B9'or pin_i=='Y4':
            self.state = False
            timer_n = 4
            channel = 4

        elif pin_i=='B13'or pin_i=='Y6':
            self.state = True
            timer_n = 1
            channel = 1


        elif pin_i=='B14'or pin_i=='Y7':
            self.state = True
            timer_n = 1
            channel = 2
        elif pin_i=='B15'or pin_i=='Y8':
            self.state = True
            timer_n = 1
            channel = 3

        elif pin_i=='C6'or pin_i=='Y1':
            self.state = False

            timer_n = 8
            channel = 1

        elif pin_i=='C7'or pin_i=='Y2':
            self.state = False
            timer_n = 8
            channel = 2
        self.timer = Timer(timer_n, freq=freq)
        self.ch = self.timer.channel(channel, Timer.PWM, pin=self.pin)#
        self.pwm_write(0)

    def pwm_write(self,percent):
        if self.state:
            self.ch.pulse_width_percent(100-percent)
        else:
            self.ch.pulse_width_percent(percent)


# class Encoder(object):
#     def __init__(self, clk, dt, reverse, scale):
#         self.reverse = reverse
#         self.scale = scale
#         self.forward = True
#         pin_x = pyb.Pin(clk)
#         pin_y = pyb.Pin(dt)
#         self.pin_x = pin_x
#         self.pin_y = pin_y
#         self._pos = 0
#         self.x_interrupt = pyb.ExtInt(pin_x, pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_NONE, self.x_callback)
#         self.y_interrupt = pyb.ExtInt(pin_y, pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_NONE, self.y_callback)
#         self.timer_x = 0
#         self.timer_y = 0
#
#     def x_callback(self, line):
#         if utime.ticks_us() - self.timer_x >= 50:
#             self.timer_x = utime.ticks_us()
#             self.forward = self.pin_x.value() ^ self.pin_y.value() ^ self.reverse
#             self._pos += 1 if self.forward else -1
#
#     def y_callback(self, line):
#         if utime.ticks_us() - self.timer_Y >= 50:
#             self.timer_Y = utime.ticks_us()
#             self.forward = self.pin_x.value() ^ self.pin_y.value() ^ self.reverse ^ 1
#             self._pos += 1 if self.forward else -1
#
#     #@property
#
#     def position(self):
#         return self._pos * self.scale
#
#     def reset(self):
#         self._pos = 0


#----------------------------------------------------------------------
ENC_STATES = (
    0,   # 00 00
    -1,  # 00 01
    1,   # 00 10
    0,   # 00 11
    1,   # 01 00
    0,   # 01 01
    0,   # 01 10
    -1,  # 01 11
    -1,  # 10 00
    0,   # 10 01
    0,   # 10 10
    1,   # 10 11
    0,   # 11 00
    1,   # 11 01
    -1,  # 11 10
    0    # 11 11
)
ACCEL_THRESHOLD = const(5)


class Encoder_new(object):
    def __init__(self, pin_clk, pin_dt,clicks=1,
                 min_val=0, max_val=10000, accel=0, reverse=False):

        self.pin_clk = pyb.Pin(pin_clk)
        self.pin_dt = pyb.Pin(pin_dt)



        self.min_val = min_val * clicks
        self.max_val = max_val * clicks
        self.accel = int((max_val - min_val) / 100 * accel)
        self.max_accel = int((max_val - min_val) / 2)
        self.clicks = clicks
        self.reverse = 1 if reverse else -1

        # The following variables are assigned to in the interrupt callback,
        # so we have to allocate them here.
        self._value = 0
        self._readings = 0
        self._state = 0
        self.cur_accel = 0

        self.set_callbacks(self._callback)

    def _callback(self, line):
        self._readings = (self._readings << 2 | self.pin_clk.value() << 1 |
                          self.pin_dt.value()) & 0x0f

        self._state = ENC_STATES[self._readings] * self.reverse

        if self._state:
            self.cur_accel = min(self.max_accel, self.cur_accel + self.accel)

            self._value = min(self.max_val, max(self.min_val, self._value +
                              (1 + (self.cur_accel >> ACCEL_THRESHOLD)) *
                              self._state))

    def set_callbacks(self, callback=None):
        #mode = Pin.IRQ_RISING | Pin.IRQ_FALLING
        # self.irq_clk = self.pin_clk.irq(trigger=mode, handler=callback)
        # self.irq_dt = self.pin_dt.irq(trigger=mode, handler=callback)

        self.x_interrupt = pyb.ExtInt( self.pin_clk, pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_NONE, callback)
        self.y_interrupt = pyb.ExtInt(self.pin_dt, pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_NONE, callback)

    def close(self):
        self.set_callbacks(None)
        self.irq_clk = self.irq_dt = None

    @property
    def value(self):
        return self._value // self.clicks

    def reset(self):
        self._value = 0



#------------------------------------------------------------------------




class Motor_shild:
    def __init__(self,DirPin,PWM_A='Y6',PWM_B='Y7',encoder=False,PinEnc=None,revers1=True,revers2=True):
        self.len_pin=0
        if len(DirPin) == 4:
            self.DirA_1 = Pin(DirPin[0], Pin.OUT_PP)
            self.DirA_2 = Pin(DirPin[1], Pin.OUT_PP)
            self.DirB_1 = Pin(DirPin[2], Pin.OUT_PP)
            self.DirB_2 = Pin(DirPin[3], Pin.OUT_PP)
            self.len_pin=4
        elif len(DirPin) == 2:
            self.DirA_1 = Pin(DirPin[0], Pin.OUT_PP)
            self.DirB_1 = Pin(DirPin[1], Pin.OUT_PP)
            self.len_pin=2

        self.pwm1=PWM(PWM_A,5000)
        self.pwm2=PWM(PWM_B,5000)
        #
        # self.S1 = 0
        # self.S2 = 0
        # self.S3 = 0
        #self.S_data=[]

        # self.eold=0
        # self.u=0
        # self.e=0
        # self.Z=0

        self.Pd_done=True
        self.naprA = 0
        self.naprB = 0
        self.napr_RL = (0, 0, 0, 0)
        self.RL = 0

        if encoder:
            # self.ENC2 = Encoder(PinEnc[2], PinEnc[3], revers2,1)
            self.ENC1 = Encoder_new(PinEnc[0], PinEnc[1], min_val=-1000000, max_val=1000000, reverse=revers1)
            self.ENC2 = Encoder_new(PinEnc[2], PinEnc[3], min_val=-1000000, max_val=1000000, reverse=revers2)
            self.lastval = 0

        self.pwm1.pwm_write(0)
        self.pwm2.pwm_write(0)

        self.Eold =0
        self.revers_enc1=0
        self.revers_enc2 = 0

    # def naprav_motors(self,napr):
    #
    #     if self.Pd_done:
    #         self.RL = 0
    #         self.napr=napr
    #         if self.napr[0]:self.DirA_1.high()
    #         else:self.DirA_1.low()
    #         if self.napr[1]:self.DirA_2.high()
    #         else:self.DirA_2.low()
    #         if self.napr[2]:self.DirB_1.high()
    #         else:self.DirB_1.low()
    #         if self.napr[3]:self.DirB_2.high()
    #         else:self.DirB_2.low()

    def np_motorA(self,napr):

        self.RL = 0
        self.naprA=napr
        if self.len_pin == 4:
            if self.naprA==1:
                self.DirA_1.high();#print(1)
                self.DirA_2.low();  # print(0)
            elif self.naprA==2 :
                self.DirA_1.low();#print(0)
                self.DirA_2.high();  # print(0)

        elif self.len_pin==2:
            if self.naprA == 1:
                self.DirA_1.high();  # print(1)
            elif self.naprA == 2:
                self.DirA_1.low();  # print(0)


    def np_motorB(self, napr):

        self.RL = 0
        self.naprB = napr
        if self.len_pin == 4:
            if self.naprB == 1:
                self.DirB_1.high();  # print(1)
                self.DirB_2.low();  # print(0)
            elif self.naprB == 2:
                self.DirB_1.low();  # print(0)
                self.DirB_2.high();  # print(1)
        elif self.len_pin == 2:
            if self.naprB == 1:
                self.DirB_1.high();  # print(1)
            elif self.naprB == 2:
                self.DirB_1.low();  # print(0)

        # print("B--------------------------" )
    def MotorStop(self,motor):
        if motor=="A":
            self.pwm1.pwm_write(0)
        if motor=="B":
            self.pwm2.pwm_write(0)

    def MotorMove(self, motor, speed, RL=1):
        if motor == "A":

            if speed < 0:
                if RL == 1:
                    RL = 2
                elif RL == 2:
                    RL = 1
                self.np_motorA(RL)
                # print(math.fabs(speed))
                self.pwm1.pwm_write(math.fabs(speed))

            else:
                self.np_motorA(RL)
                self.pwm1.pwm_write(speed)


        elif motor == "B":

            if speed < 0:
                if RL == 1:
                    RL = 2
                elif RL == 2:
                    RL = 1
                self.np_motorB(RL)
                self.pwm2.pwm_write(math.fabs(speed))
            else:
                self.np_motorB(RL)
                self.pwm2.pwm_write(speed)

    def DegryCount(self,ENC,ls=4.2):
        val=0
        if ENC=="A":
            # val = self.ENC1.position()
            val = self.ENC1.value
        elif ENC=="B":
            # val = self.ENC2.position()
            val = self.ENC2.value
        if self.lastval != val:
            self.lastval = val
        return val//ls

    def DegryReset(self,motor):
        if motor=='A':
              self.ENC1.reset()
        elif motor=='B':
              self.ENC2.reset()

    def MoveDegery(self,speed1,speed2,degery1,degery2,ls=4.2):
            i=1
            dt1, val_1 = False, self.DegryCount('A',ls)
            dt2, val_2 = False, self.DegryCount('B',ls)
            u1 = int((degery1-val_1)*1)
            u2 = int((degery2-val_2)*1)
            n =  2 if speed1 > 70 else 1
            if u1*0.5<i and u1*0.5>(-i):
                    speed1=speed1//n

            if u1 >i:
                    self.MotorMove('A', speed1)

            elif u1 < i:

                    self.MotorMove('A', speed1*(-1))

            if interval(u1,-i,i):
                    dt1 = True
                    self.pwm1.pwm_write(0)
            elif degery1 == 0:dt1 = True

            #-----------------------------------

            if u2 >i:
                    self.MotorMove('B', speed2)
            elif u2 < i:
                    self.MotorMove('B', speed2*(-1))

            if interval(u2,-i,i):
                    dt2 = True
                    self.pwm2.pwm_write(0)
            elif degery2 == 0:dt2 = True

            if dt1 and dt2:
                return int(u1),int(u2),False

            else:
                return int(u1),int(u2),True


    def DegerySync(self,speed,kp,kd):
        val_1 = self.DegryCount('A',1)
        val_2 = self.DegryCount('B',1)
        speed_n = speed

        E = (self.revers_enc1-val_1) - (self.revers_enc2-val_2) if speed < 0 else val_1 - val_2
        #print(((self.revers_enc1-val_1) ,(self.revers_enc2-val_2)) if speed < 0 else (val_1 , val_2))

        Ye = (E * kp + (E - self.Eold) * kd)  # // 100

        m1 = constrain(math.fabs(speed) - Ye, 0, math.fabs(speed))
        m2 = constrain(math.fabs(speed) + Ye, 0, math.fabs(speed))
        # m1 = constrain(speed - Ye, 0, speed)
        # m2 = constrain(speed + Ye, 0, speed)

        #print(int(val_1 ),int(val_2 ),Ye)
        if interval(Ye,-60,60)  :
            m2 = constrain(m2, 0, 66)
            m1 = constrain(m2, 0, 66)

        if speed_n < 0:

            self.MotorMove('A', m2,2)
            self.MotorMove('B', m1,2)


        else:

            self.MotorMove('A', m2)
            self.MotorMove('B', m1)
            self.revers_enc1 = val_1
            self.revers_enc2 = val_2



        self.Eold = E


    def motor_sync(self,degry,speed):
        val_1 = self.DegryCount('A',2)
        val_2 = self.DegryCount('B',2)
        print(val_1,val_2,"GOLS",degry)

        if val_1>degry :
            self.MotorMove('A', math.fabs(speed),2)

        elif val_1<degry :
            self.MotorMove('A',math.fabs(speed))

        if val_2<degry :
            self.MotorMove('B', math.fabs(speed))
        elif val_2>degry :
            self.MotorMove('B', math.fabs(speed),2)

        if val_1==degry and val_2==degry:
            self.MotorStop('A')
            self.MotorStop('B')
            return True
        else:
            return False





class Motor:
    def __init__(self,pwm,Dir,Encoder_pin=None,revers=True):


        self.pwm = PWM(pwm)
        # if len(Dir) ==2:
        #     self.dirs1=Pin(Dir[0], Pin.OUT_PP)
        #     self.dirs2 = Pin(Dir[1], Pin.OUT_PP)
        # else:
        self.dirs = Pin(Dir, Pin.OUT_PP)
        self.encoder=None
        if Encoder_pin:
            self.encoder = Encoder_new(Encoder_pin[0], Encoder_pin[1],min_val=-100000, max_val=100000, reverse=revers)

        self.lastval=0
        #print(self.encoder.value)

    def move(self,speed):
        if speed < 0:
            self.dirs.high()
        else:
            self.dirs.low()
        self.pwm.pwm_write(math.fabs(speed))

    def enc_count(self):
        val= self.encoder.value
        if self.lastval != val:
            self.lastval = val
        return val



    def reset(self):
        self.encoder.reset()
    def encode_move(self,enc,speed,Kp=1):
        #val = self.encoder.value

        val=self.enc_count()

        u=(enc- val)*Kp
        u=constrain(u,-speed,speed)
        if interval(u,-5,5):
                if speed<0:
                    u-=9
                else:
                    u+=9

        self.move(u)

    def stop(self):
        self.move(0)
    # def PD_reg_inc(self,speed, p_data, d_data, S_data,zachita,M_A=10,M_B=30,datchic=2):
    #     if self.Pd_done:
    #         self.speed=speed
    #         self.S_data=S_data
    #
    #         if datchic==2:
    #             self.S1 = self.S_data[0]
    #             self.S2 = self.S_data[1]
    #             self.e=self.S1-self.S2
    #         elif datchic==3:
    #             self.S1 = self.S_data[0]
    #             self.S2 = self.S_data[1]
    #             self.S3 = self.S_data[2]
    #             self.e = (self.S1 * 10 + self.S2 * 20 + self.S3 * 30) / (self.S1 + self.S2 + self.S3) - 20
    #         self.e=math.fabs(self.e)
    #
    #         self.u=self.e*p_data+(self.e-self.eold)*d_data
    #         self.eold=self.e
    #
    #
    #         if datchic == 3:
    #             if self.S1 > zachita: self.Z = 1
    #             elif self.S2 > zachita: self.Z = 2
    #             if self.S3 < 60:
    #                 if self.Z == 1:
    #                     state = "A"
    #                     self.pwm1.pwm_write(50)
    #                     self.pwm2.pwm_write(30)
    #                 if self.Z == 2:
    #                     state = "B"
    #                     self.pwm1.pwm_write(30)
    #                     self.pwm2.pwm_write(50)
    #             elif self.S3 < 30:
    #                 if self.Z == 1:
    #                     state = "A"
    #                     self.pwm1.pwm_write(50)
    #                     self.cpwm2.pwm_write(20)
    #                 if self.Z == 2:
    #                     state = "B"
    #                     self.pwm1.pwm_write(20)
    #                     self.cpwm2.pwm_write(50)
    #
    #             else:
    #                 self.pwm1.pwm_write(constrain(speed - self.u, 0, speed))
    #                 self.pwm2.pwm_write(constrain(speed + self.u, 0, speed))
    #
    #         elif datchic == 2:
    #             if self.S1 > zachita: self.Z = 1
    #             elif self.S2 > zachita: self.Z = 2
    #             elif self.S1<zachita and self.S2<zachita:self.Z=0
    #
    #             if self.Z==1:
    #                 self.pwm1.pwm_write(speed-M_A)
    #                 self.pwm2.pwm_write(speed-M_B)
    #
    #             elif  self.Z==2:
    #                 self.pwm1.pwm_write(speed-M_B)
    #                 self.pwm2.pwm_write(speed-M_A)
    #             else:
    #                 self.pwm1.pwm_write(constrain(speed - self.u, 0, speed))
    #                 self.pwm2.pwm_write(constrain(speed + self.u, 0, speed))
    #
