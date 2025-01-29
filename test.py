import time
import brickpi3

import sys
RL_INBALANCE_OFFSET = float(sys.argv[1]) if len(sys.argv)>1 else 0

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B # right motor
motorL= BP.PORT_C # left motor
ROTS_FWD = 4.244 + RL_INBALANCE_OFFSET
ROTS_TURN = 1.142 - 0.015

try:
    BP.offset_motor_encoder(motorL, BP.get_motor_encoder(motorL))
    BP.offset_motor_encoder(motorR, BP.get_motor_encoder(motorR))

    for _ in range(4):
        BP.set_motor_limits(motorL, power=20)
        BP.set_motor_limits(motorR, power=20*RL_INBALANCE_OFFSET)
        BP.set_motor_position_relative(motorL, 360 * ROTS_FWD)
        BP.set_motor_position_relative(motorR, 360 * ROTS_FWD)

        time.sleep(10)
        print("Finished fwd")
        BP.set_motor_limits(motorL, power=20)
        BP.set_motor_limits(motorR, power=20*RL_INBALANCE_OFFSET)
        BP.set_motor_position_relative(motorL, 360 * ROTS_TURN)
        BP.set_motor_position_relative(motorR, -360 * ROTS_TURN)

        time.sleep(4.5)
        print("Finished rotating")
except Exception as e:
    print("Error: ", e)

BP.reset_all()