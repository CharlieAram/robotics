import time
import brickpi3

import sys
diff = eval(" ".join(sys.argv[1:])) if len(sys.argv)>1 else 0

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

try:
    BP.offset_motor_encoder(motorL, BP.get_motor_encoder(motorL))
    BP.offset_motor_encoder(motorR, BP.get_motor_encoder(motorR))

    for ROTS_FWD,ROTS_TURN in zip(ROTS,ROTST):
        BP.set_motor_limits(motorL, power=POWER)
        BP.set_motor_limits(motorR, power=POWER)
        BP.set_motor_position_relative(motorL, 360 * ROTS_FWD)
        BP.set_motor_position_relative(motorR, 360 * ROTS_FWD)

        for i in range(10):
            print(BP.get_motor_encoder(motorL))
            print(BP.get_motor_encoder(motorR))
            time.sleep(0.4)
        print("Finished fwd")


        BP.set_motor_limits(motorL, power=POWER)
        BP.set_motor_limits(motorR, power=POWER)
        BP.set_motor_position_relative(motorL, 360 * ROTS_TURN)
        BP.set_motor_position_relative(motorR, -360 * ROTS_TURN)
        for i in range(5):
            print(BP.get_motor_encoder(motorL))
            print(BP.get_motor_encoder(motorR))
            time.sleep(0.4)

        print("Finished rotating")
except:
    print("Error")

BP.reset_all()