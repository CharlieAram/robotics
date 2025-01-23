
import time
import brickpi3

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B # right motor
motorL = BP.PORT_C # left motor
speed = 200 # range is -255 to 255, make lower if bot it too fast

def rotate_multiple(port, rots, wait=0.5, divisions=3, opposite = None):
    while rots >= 1:
        for _ in range(divisions):
            BP.set_motor_position_relative(port, 360 / divisions)
            if opposite:
                BP.set_motor_position_relative(opposite, -360 / divisions)
            time.sleep(wait)
    BP.set_motor_position_relative(port, 360 * rots)
    if opposite:
        BP.set_motor_position_relative(opposite, -360 * rots)
    time.sleep(wait)
    

def forward(rots: float):
    # TODO: Test this! Might have to set for each rotation, not sure yet
    rotate_multiple(motorL & motorR, rots)

def turn(rots: float):
    rotate_multiple(motorL, rots, opposite=motorR)

ROTS_FWD = 4.244
ROTS_TURN = 1.142

for _ in range(4):
    forward(ROTS_FWD)
    turn(ROTS_TURN)