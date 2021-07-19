#!/usr/bin/env python3
# coding: utf-8

import socket,time
import cv2
import sys
import argparse
import zmq
#import video_grabber

import time
from threading import Thread
import fcntl
import numpy as np
import zlib
import base64
import subprocess
import pickle
import asyncio
import os
import pty
import json
import select
#import mpu9250
#from io import StringIO



#
# import RobotAPI as rapi
# robot = rapi.RobotAPI(flag_video=False)

# print("Start RAW")

os.system('sudo modprobe bcm2835-v4l2')

#parser = argparse.ArgumentParser()
# parser.add_argument('--port', type=int, help='The port on which the server is listening', required=True)
#parser.add_argument('--jpeg_quality', type=int, help='The JPEG quality for compressing the reply', default=50)
#parser.add_argument('--encoder', type=str, choices=['cv2','turbo'], help='Which library to use to encode/decode in JPEG the images', default='turbo')
log=[]
class error(object):
    def write(self,data):
        log.append(data)


class AdamServer(Thread):
    def __init__(self,port):
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = ''

        self.console_out = ""
        self.proc = False
        self.filename = "bot.py"
        #self.filename = "TESTADAMFAILE.py"
        # raspberry
        self.dir = "/home/pi/"
        self.OFLAGS = None

        self.message=''
        self.start_file = True

        self.master, self.slave =pty.openpty()
        self.set_nonblocking(self.master)

        self.proc=None
        self.flag_run_file=False
        self.LOG=''
        self.address=(0,'')

        self.server_address = (host, port)
        self.sock.bind(self.server_address)


        self.my_thread_udp = Thread(target=self.udp_comand)
        #self.my_thread_udp.daemon = True
        self.my_thread_udp.start()
        self.my_thread_udp.join(0.005)

        #self.mpu = mpu9250.mpu9250()

        self.readProces=False
        self.stderr_fileno = sys.stderr


        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_server())
        loop.close()  # prevents annoying signal handler error

    def set_nonblocking(self,file_handle):
        """Make a file_handle non-blocking."""

        self.OFLAGS = fcntl.fcntl(file_handle, fcntl.F_GETFL)
        nflags = self.OFLAGS  | os.O_NONBLOCK
        fcntl.fcntl(file_handle, fcntl.F_SETFL, nflags)

    def udp_comand(self):

        # клиент к демону
        flag_no_data = False
        flag_data=False
        flag_fail_name=False
        file_enc=['','']
        flag_video=False

        print('recive server')
        while True:
            try:
                ready = select.select([self.sock], [], [], 0.005)
                if ready[0]:
                    dat,self.address = self.sock.recvfrom(65507)
                    data=zlib.decompress(dat)


                    if data==b'scan':
                        print("CONECT !!!!")
                        self.sock.sendto(b'CONECT', self.address)

                    if flag_fail_name:
                           #d = zlib.decompress(data)
                           #print(d.decode('utf-8'))

                           #file_enc[0]=d.decode('utf-8')
                           file_enc[0] = data.decode('utf-8')
                           flag_fail_name=False

                    elif data == b"nf":
                         flag_fail_name=True

                    #elif data[0] == ord("f"):
                    elif flag_data:

                        #d = zlib.decompress(data)
                        #file_enc[1]=d.decode('utf-8')
                        file_enc[1] = data.decode('utf-8')
                        #print(file_enc[0],file_enc[1])

                        flag_data=False


                    elif data == b"f":
                        flag_data=True
                        flag_no_data = False


                    #elif len(file_enc)>0:
                    elif flag_video :
                        #v = zlib.decompress(data)
                        #command = v.decode('utf-8')
                        command = data.decode('utf-8')

                        if command == 'vidOff':
                            print('vidOff')
                            my_file = open(self.dir + "LOG.txt", 'w')
                            my_file.write('video_off')
                            my_file.close()
                            self.sock.sendto(b'video off', self.address)

                        elif  command[:5]   == 'vidOn':
                            print('vidOn'+command[5:] )
                            my_file = open(self.dir + "LOG.txt", 'w')
                            my_file.write('video_on'+command[5:] )
                            my_file.close()
                            self.sock.sendto(b'video on', self.address)
                        flag_video=False

                    elif data == b"vid":
                        flag_video = True

                    elif data == b"start" and self.start_file:
                        print("UDP START" )
                        self.message = "start"
                        self.sock.sendto(b'file start', self.address)



                    elif data == b"stop":
                        self.message = "stop"
                        self.sock.sendto(b'file stop', self.address)

                    elif data == b"reset":
                        subprocess.Popen(["sudo", "reboot"])

                    else:
                        self.message='...'


                    if file_enc[0] :

                        text = file_enc[0].split('.')
                        if len(text)>1:
                            if text[1] == 'py' and file_enc[1] and not self.flag_run_file:
                                self.filename = file_enc[0]

                                with open(self.dir + self.filename, 'w') as f:
                                    f.write(file_enc[1])
                                print(self.proc)

                                #print(file_enc[1])
                                self.message = "start"
                                time.sleep(0.1)
                                file_enc = ['', '']
                                self.flag_run_file=True

                    if self.address and self.flag_run_file:
                             self.sock.sendto(("START FAIL "+self.filename+'|').encode('utf-8'), self.address)

                    data=None
            except Exception as e:
                print('Errors jast',e)


    def decompress(self,obj):
        res = True
        file_data = b''
        try:
            print("dec data", obj)
            file_data = zlib.decompress(obj)
        except:
            print("error decompress")
            res = False
            exit(0)
        return res, file_data




    def run_file(self):

        self.proc  = subprocess.Popen(['python3',self.dir+ self.filename,"&"], stdout=subprocess.PIPE,  stderr=subprocess.STDOUT)#, stderr=subprocess.STDOUT..sys.executable
        t = Thread(target=self.output_reader, args=(self.proc,))
        t.start()
        t.join(0.01)

        #self.console_out = self.proc.stdout.read().decode("utf-8")
        #print("RUN PROCESS", self.proc)
        #data=self.proc.communicate()
        #print(self.console_out)
        #self.proc = False

    async def output_reader(self):
        stdout, stderr = await self.proc.communicate()
        print("ERROR", stderr.decode().strip())
        # for _ in range(2):
        # for line in iter(proc.stdout.readline, b''):
        #     print('got line: {0}'.format(line.decode('utf-8')), end='')
        #     try:
        #         self.sock.sendto(line, self.address)
        #     except Exception as e:print('ERROR SERVER',e)

    async def run_subprocess_read(self):
        if self.proc:
            if self.proc.returncode == None:
                # s = stdout.readline()
                # print("read..")
                s = ""
                try:
                    # return 1-n bytes or exception if no bytes
                    s = str(os.read(self.master, 4096).decode("utf-8"))
                    print("MESEEG ",s)

                except BlockingIOError:
                    # sys.stdout.write('no data read\r')
                    #   print("block")
                    pass

                # print("..ok")
                # if s.find("EXIT")>=0:
                #     print("end of programm")
                #     proc=False
                self.console_out += s
                return s


    async def run_subprocess(self):
        print('start FILES')
        # asyncio.ensure_future(self.run_subprocess())
        # await asyncio.sleep(0.05)
        self.proc = await asyncio.create_subprocess_exec(
            'python3', self.dir +self.filename,stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE )#
        await asyncio.sleep(0.002)
        stdout, stderr = await self.proc.communicate()

        # sys.stderr=error()

        print('start COMUNICATE')


        #
        # if stdout:
        #     print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            pass
        #    print(f'[stderr]\n{stderr.decode()}')


        print('START FILE', self.filename)
        #print(data)


        time.sleep(0.5)
        self.start_file = True
        self.flag_run_file = False
        #self.proc=False



        print("END proc",self.flag_run_file)

    async def run_server(self):

        asyncio.ensure_future(self.run_subprocess())
        await asyncio.sleep(0.001)

        while True:

            if self.message=="start" :
                print("stop")
                self.readProces = False
                if self.proc :
                    #print("TGGG",self.proc.returncode)
                    if self.proc.returncode==None:
                        self.proc.kill()

                asyncio.ensure_future(self.run_subprocess())


                print("start ok")
                self.message=""

            if self.message=="data" :
                asyncio.ensure_future(self.run_subprocess_read())

            if self.message=="stop" :
             #=================================
                print("stop")
                self.readProces = False
                if self.proc:
                    self.proc.kill()

            await asyncio.sleep(0.002)




if __name__ =='__main__':
        server=AdamServer(4999)



