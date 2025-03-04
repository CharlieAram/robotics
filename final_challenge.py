import motor_driver
import brickpi3
import time
import sys

POWER = eval(" ".join(sys.argv[1:])) if len(sys.argv) > 1 else 100



if __name__ == "__main__":
    motorR = brickpi3.BrickPi3.PORT_B  # right motor
    motorL = brickpi3.BrickPi3.PORT_C  # left motor
    driver = motor_driver.MotorDriver(motorL=motorL, motorR=motorR)
    driver.flipR = True
    print(POWER)
    driver.write_left(POWER)
    driver.write_right(POWER)
    # for i in range(0, 255):
    #     print(i)
    #     driver.write_left(i)
    #     driver.write_right(i)
    #     time.sleep(0.2)
