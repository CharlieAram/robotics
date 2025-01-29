import time
import brickpi3

import sys
SCALE = eval(" ".join(sys.argv[1:])) if len(sys.argv)>1 else 2

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B # right motor
motorL= BP.PORT_C # left motor
ROTS_FWD = 4.244 * (38/42.5) * 1.12
ROTS = [ROTS_FWD, ROTS_FWD * 40/42.5] * 2
ROTS[2] *= 0.93
ROTS_TURN = 1.142 - 0.015
ROTST = [ROTS_TURN] * 4
ROTST[1] *= 1.045

try:

    for ROTS_FWD,ROTS_TURN in zip(ROTS,ROTST):
        BP.offset_motor_encoder(motorL, BP.get_motor_encoder(motorL))
        BP.offset_motor_encoder(motorR, BP.get_motor_encoder(motorR))

        targetL = 360*ROTS_FWD
        targetR = 360*ROTS_FWD

        BP.set_motor_power(motorL, 20 * SCALE)
        BP.set_motor_power(motorR, 20 * SCALE)

        l=BP.get_motor_encoder(motorL)
        r=BP.get_motor_encoder(motorR)
        t = time.time()
        while (l < targetL or r < targetR):
            if l < targetL and r < targetR and time.time() - t > 0.4:
                ratio = (l-r) / 10
                print(ratio)
                BP.set_motor_power(motorL, (20 - ratio) * SCALE)
                BP.set_motor_power(motorR, (20 + ratio) * SCALE)
                t = time.time()

            l=BP.get_motor_encoder(motorL)
            r=BP.get_motor_encoder(motorR)
            if l >= targetL:
                BP.set_motor_power(motorL, 0)
            if r >= targetR:
                BP.set_motor_power(motorR, 0)

        print("Finished fwd")

        BP.offset_motor_encoder(motorL, BP.get_motor_encoder(motorL))
        BP.offset_motor_encoder(motorR, BP.get_motor_encoder(motorR))

        BP.set_motor_power(motorL, 20 * SCALE)
        BP.set_motor_power(motorR, -20 * SCALE)

        targetL = ROTS_TURN * 360
        targetR = ROTS_TURN * 360

        l=BP.get_motor_encoder(motorL)
        r=-BP.get_motor_encoder(motorR)
        t = time.time()
        while (l < targetL or r < targetR):
            print(l, r, targetL, targetR)
            if l < targetL and r < targetR and time.time() - t > 0.4:
                ratio = (l-r) / 10
                print(ratio)
                BP.set_motor_power(motorL, (20 - ratio) * SCALE)
                BP.set_motor_power(motorR, - (20 + ratio) * SCALE)
                t = time.time()

            l=BP.get_motor_encoder(motorL)
            r=-BP.get_motor_encoder(motorR)
            if l >= targetL:
                BP.set_motor_power(motorL, 0)
            if r >= targetR:
                BP.set_motor_power(motorR, 0)
        print("Finished rotating",l,r)
except:
    print("Error")

BP.reset_all()