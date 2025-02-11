import brickpi3  # import BrickPi.py file to use BrickPi operations

import curses  # import curses for text processing
import time

# set up curses interface

stdscr = curses.initscr()
curses.noecho()

BP = (
    brickpi3.BrickPi3()
)  # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B  # right motor
motorL = BP.PORT_C  # left motor
speed = 200  # range is -255 to 255, make lower if bot it too fast


def stop():
    BP.set_motor_power(motorR, 0)
    BP.set_motor_power(motorL, 0)


if __name__ == "__main__":
    degrees = [90 * i for i in range(25)]
    try:
        for degree in degrees:
            BP.set_motor_position(motorR, degree)
            BP.set_motor_position(motorL, -degree)

            print("degree: ", degree)

            input("Press Enter to continue...")
            # inp = stdscr.getkey() #Take input from the terminal

            # if inp == 'q':
            #     break
            # else:
            #     pass

            time.sleep(5)

    except (
        KeyboardInterrupt
    ):  # except the program gets interrupted by Ctrl+C on the keyboard.
        stop()
        curses.endwin()  # Reset terminal
        print("Keyboard Interrupt")
