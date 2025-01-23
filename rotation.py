
import brickpi3

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B # right motor
motorL = BP.PORT_C # left motor
speed = 200 # range is -255 to 255, make lower if bot it too fast


def forward(rots: float):
    # TODO: Test this! Might have to set for each rotation, not sure yet
    BP.set_motor_position(motorL & motorR, 360 * rots)

def turn(rots: float):
    BP.set_motor_position(motorL, 360 * rots)
    BP.set_motor_position(motorR, -360 * rots)

ROTS_FWD = 4.244
ROTS_TURN = 1.142

for _ in range(4):
    forward(ROTS_FWD)
    turn(ROTS_TURN)