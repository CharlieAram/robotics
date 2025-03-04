import motor_driver
import brickpi3


if __name__ == "__main__":
    motorR = brickpi3.BrickPi3.PORT_B  # right motor
    motorL = brickpi3.BrickPi3.PORT_C  # left motor
    driver = motor_driver.MotorDriver(motorL=motorL, motorR=motorR)
    driver.lane_change()
