# File description

On our robot we have 2 files that work at the same time. File main.py is launched on pyboard, it get's the data from raspberry and controls servo drive and motor. osnov.py(for final attempts) or kwala.py(for qualification) is launched on raspberry, it receives the image from camera, processes it, and sends data to pyboard.
RobotAPI.py - library, that is used on raspberry to help get an image from camera and display it while debugging.
autostart.py - file on raspberry, for auto launching of the program after turning on.
module.py - library on pyboard. It's used to help controling servo and motor.

# Main.py

main.py is a program on pyboard. First of all, it waits  for a button to be pressed, than it gets the speed, and an angle for servo drive. Than it passes the speed directly to motor. And uses a proportional-derivative controller(https://en.wikipedia.org/wiki/PID_controller) to regulate the speed of the servo and set to the needed angle. 

# kwala.py

kwala.py is a program on raspberry. After it gets the image from camera, it cuts out 3 areas on it, 1 on the right side, 1 on the left, and at the bottom. The program converts them from the bgr color model to hsv, and findes the needed items on it. The ones on the left and right are used to detect the walls. After detection it uses the proportional-derivative controller to help robot move in the center between 2 walls. Then if we see 1 wall, and don't see the other, the robot starts to to turn. The part at the bottom is used to count lines, that we have passed. When the robot passes 12 lines, it stops.

# osnov.py
osnov.py is a  program on raspberry. It's practically similar to kwala.py. It's 2 more area in it, 1 is used to detect signes, and, based on theres position, make robot go arond them. A proportional-derivative controller is also used here. The other is used to find out, in which

# Connection to pyboard

To put the programs to pyboard, you need to just connect pyboard to your computer, and it will open as a USB flash drive, then copy files main.py and module.py, wait for red LED
to turn off, and thats it, all done.

# Connection to raspberry

1)First you neeed to install some os on your raspberry. You’ll need a microSD card (go with at least 8 GB), a computer with a slot for it, and, of course, a Raspberry Pi and basic peripherals (a mouse, keyboard, screen, and power source).

First things first: hop onto your computer (Mac and PC are both fine) and download the Raspbian disc image. You can find the latest version of Raspbian on the Raspberry Pi Foundation’s website(https://www.raspberrypi.org/software/operating-systems/). Give yourself some time for this. It can easily take a half hour or more to download.

The Raspbian disc image is compressed, so you’ll need to unzip it. The file uses the ZIP64 format, so depending on how current your built-in utilities are, you need to use certain programs to unzip it. If you have any trouble, try these programs recommended by the Raspberry Pi Foundation:
Windows users, you’ll want 7-Zip.
Mac users, The Unarchiver is your best bet.
Linux users will use the appropriately named Unzip.

Next, pop your microSD card into your computer and write the disc image to it. You’ll need a specific program to do this:
Windows users, your answer is Win32 Disk Imager.
Mac users, you can use the disk utility that’s already on your machine.
Linux people, Etcher – which also works on Mac and Windows – is what the Raspberry Pi Foundation recommends.
The process of actually writing the image will be slightly different across these programs, but it’s pretty self-explanatory no matter what you’re using. Each of these programs will have you select the destination (make sure you’ve picked your microSD card!) and the disc image (the unzipped Raspbian file). Choose, double-check, and then hit the button to write.

![alt text](https://github.com/Riardon/WRO-LittleRobot/blob/98ea62df5dd35c2d285455a4992937db45a9d991/readme_photos/win32-disk-imager-raspbian.png)

Once the disc image has been written to the microSD card, you’re ready to go! Put that sucker into your Rasberry Pi, plug in the peripherals and power source, and enjoy. The current edition to Raspbian will boot directly to the desktop.(guide: https://thepi.io/how-to-install-raspbian-on-the-raspberry-pi/)

2) Now we are all done with the raspberry os, now we'll need an hdmi cable, a monitor, a power supply for raspberry, pc with ethernet port, and an ethernet cable.
connect your raspberri to pc using ethernet cable, with hdmi to the monitor, and finally power ip rasppberry.

3) Here you need to sing in(default login: pi, password: rasraspberry)

photo

4)Then use command "sudo nano /boot/config.txt", with it you will be able to edit file "config.txt".

photo

go to the bottom and add "enable_uart=1"

photo

5) Also you need to get raspberry's ip ethernet adress, so use command "ifconfig". There you'll see your your ip adrress. Write it down somewhere, we'll need it later.

photo

6) And finally we need to enable ssh on our raspberry. Use command "sudo raspi-config".

photo

You'll see a menu, go to 5'th point "Interfacing Options", press enter

![alt text](https://github.com/Riardon/WRO-LittleRobot/blob/abfd8e45297dbf68f70f8a7d682ced6558985106/readme_photos/raspi-config-interfacing-options.png)

Choose point 2 "SSH"

![alt text](https://github.com/Riardon/WRO-LittleRobot/blob/abfd8e45297dbf68f70f8a7d682ced6558985106/readme_photos/raspi-config-ssh.png)

Select "Yes", and hit enter 2 times, then Esc

photo

phtot

And we are done for now with hdmi cable, so disconnect it.

7) Now we can use raspberry only using ethernet, by ssh, but first you need to download bitvise ssh(https://www.bitvise.com/ssh-client-download).
8) After you are done with bitvise, open it. You'll see a menu, where you need to put ip address, written down by you earlier in field "host", 22 in field 
