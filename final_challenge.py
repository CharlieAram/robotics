import motor_driver
import brickpi3
import time
import sys

power = sys.argv[1]

if __name__ == "__main__":
    motorR = brickpi3.BrickPi3.PORT_B  # right motor
    motorL = brickpi3.BrickPi3.PORT_C  # left motor
    driver = motor_driver.MotorDriver(motorL=motorL, motorR=motorR)
    driver.flipR = True
    driver.write_left(power)
    driver.write_right(power)
    # for i in range(0, 255):
    #     print(i)
    #     driver.write_left(i)
    #     driver.write_right(i)
    #     time.sleep(0.2)
