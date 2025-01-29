import time
import brickpi3

import sys
_ = eval(" ".join(sys.argv[1:])) if len(sys.argv)>1 else 0

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B # right motor
motorL= BP.PORT_C # left motor
ROTS_FWD = 4.244 * (38/42.5) * 1.12
ROTS = [ROTS_FWD, ROTS_FWD * 40/42.5] * 2
ROTS[2] *= 0.93
ROTS_TURN = 1.142 - 0.015
ROTST = [ROTS_TURN] * 4
ROTST[1] *= 1.045
POWER = 20
FWD_STEPS = 20
TURN_STEPS = 10

try:
    BP.offset_motor_encoder(motorL, BP.get_motor_encoder(motorL))
    BP.offset_motor_encoder(motorR, BP.get_motor_encoder(motorR))
    BP.set_motor_limits(motorL, power=POWER)
    BP.set_motor_limits(motorR, power=POWER)
    for ROTS_FWD,ROTS_TURN in zip(ROTS,ROTST):

        for i in range(FWD_STEPS):
            diff = BP.get_motor_encoder(motorL) - BP.get_motor_encoder(motorR)
            print(BP.get_motor_encoder(motorL), BP.get_motor_encoder(motorR), diff)
            if diff < 0:
                BP.set_motor_position_relative(motorL, ((360 * ROTS_FWD) / FWD_STEPS) + diff)
                BP.set_motor_position_relative(motorR, (360 * ROTS_FWD) / FWD_STEPS)
            else:
                BP.set_motor_position_relative(motorL, (360 * ROTS_FWD) / FWD_STEPS)
                BP.set_motor_position_relative(motorR, (360 * ROTS_FWD) / FWD_STEPS + diff)
            time.sleep(10/FWD_STEPS)
        print("Finished fwd")

        for i in range(TURN_STEPS):
            BP.set_motor_position_relative(motorL, (360 * ROTS_TURN) / TURN_STEPS)
            BP.set_motor_position_relative(motorR, -(360 * ROTS_TURN) / TURN_STEPS)
            print(BP.get_motor_encoder(motorL))
            print(BP.get_motor_encoder(motorR))
            time.sleep(5/TURN_STEPS)

        print("Finished rotating")
except:
    print("Error")

BP.reset_all()