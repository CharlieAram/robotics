# Program Name: simplebot_simple.py

# ================================

# This code is for moving the simplebot

# Author     Date      Comments
# Karan      04/11/13  Initial Authoring
#
# These files have been made available online through a Creative
# Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)

# Revised by T. Cooper 12/18

# --- program updated for Python 3

# --- curses interface added for consistent input mang.

# Commands:

#       w-Move forward

#       a-Move left

#       d-Move right

#       s-Move back

#       x-Stop

# we add these libraries to give us the ability to use sleep func

# use Brick Pi 3 stuff and the curses interface (it makes input easier and consistent)

import time

import brickpi3  # import BrickPi.py file to use BrickPi operations

import curses  # import curses for text processing

# set up curses interface

stdscr = curses.initscr()
curses.noecho()

BP = (
    brickpi3.BrickPi3()
)  # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B  # right motor
motorL = BP.PORT_C  # left motor
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.NXT_ULTRASONIC)
speed = 170  # range is -255 to 255, make lower if bot it too fast
boost_speed = 100
turn_speed = 230
creep_speed = 210
# Move Forward


def fwd(power: int = speed):
    BP.set_motor_power(motorR, -power)
    BP.set_motor_power(motorL, power)


# Move Left
def left():
    BP.set_motor_power(motorR, -turn_speed)
    BP.set_motor_power(motorL, -turn_speed)


# Move Right
def right():
    BP.set_motor_power(motorR, turn_speed)
    BP.set_motor_power(motorL, turn_speed)


# Move backward
def back():
    BP.set_motor_power(motorR, speed)
    BP.set_motor_power(motorL, -speed)


# Stop
def stop():
    BP.set_motor_power(motorR, 0)
    BP.set_motor_power(motorL, 0)

def read_sensor():
    try:
        return (BP.get_sensor(BP.PORT_1)+ 10) #10 is offset to account for the fact that the sensor is not at the center of the robot. idek chief if 10 is accurate
    except brickpi3.SensorError:
        return 999 

# def boost():
#         BP.set_motor_power(motorR, -boost_speed)
#         BP.set_motor_power(motorL, -boost_speed)

try:
    while True:
        inp = stdscr.getkey()  # Take input from the terminal
        # Move the bot
        if inp == "s":
            fwd()
            print("fwd")

        elif inp == "a":
            left()
            print("left")

        elif inp == "d":
            right()
            print("right")

        elif inp == "w":
            back()
            print("back")

        elif inp == "/" or inp == "x":
            stop()
            print("stop")

        elif inp == "b":
            fwd(boost_speed)
            print("boost")

        elif inp == "c":
            inp2 = "a"
            fwd(creep_speed)
            print("creep")
            while inp2 != "c":
                print(read_sensor())
                inp2 = stdscr.getkey()
                time.sleep(0.05)
            stop()
        time.sleep(0.01)  # sleep for 10 ms
except KeyboardInterrupt:
    BP.reset_all()
    curses.endwin()  # Reset terminal
    print("Keyboard Interrupt")
