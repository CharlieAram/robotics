import atexit
import time
import brickpi3

import sys

SCALE = eval(" ".join(sys.argv[1:])) if len(sys.argv) > 1 else 10


class MotorDriver:
    def __init__(self, motorL, motorR, scale=1):
        self.SCALE = scale
        self.BP = brickpi3.BrickPi3()
        atexit.register(self.BP.reset_all)
        self.motorL = motorL
        self.motorR = motorR
        self.flipL = self.flipR = False
        self.sensor = self.BP.PORT_1
        self.BP.set_sensor_type(self.sensor, self.BP.SENSOR_TYPE.NXT_ULTRASONIC)

    def read_left(self):
        res = self.BP.get_motor_encoder(self.motorL)
        if self.flipL:
            return -res
        return res

    def read_right(self):
        res = self.BP.get_motor_encoder(self.motorR)
        if self.flipR:
            return -res
        return res

    def read(self):
        return self.read_left(), self.read_right()

    def read_sensor(self):
        try:
            return (
                self.BP.get_sensor(self.sensor) + 5
            )  # 10 is offset to account for the fact that the sensor is not at the center of the robot. idek chief if 10 is accurate
        except brickpi3.SensorError:
            return None

    def write_left(self, val):
        if self.flipL:
            val = -val
        self.BP.set_motor_power(self.motorL, val)

    def write_right(self, val):
        if self.flipR:
            val = -val
        self.BP.set_motor_power(self.motorR, val)

    def move_forward(self, dist: float):
        """
        Move the robot forward by a distance dist (in rotations)
        """
        self.BP.offset_motor_encoder(
            self.motorL, self.BP.get_motor_encoder(self.motorL)
        )
        self.BP.offset_motor_encoder(
            self.motorR, self.BP.get_motor_encoder(self.motorR)
        )

        targetL = 360 * dist
        targetR = 360 * dist

        self.write_left(20 * self.SCALE)
        self.write_right(20 * self.SCALE)

        l, r = self.read()
        t = time.time()
        while l < targetL or r < targetR:
            if l < targetL and r < targetR and time.time() - t > 0.4:
                ratio = (l - r) / 10
                print(ratio)
                self.write_left((20 - ratio) * self.SCALE)
                self.write_right((20 + ratio) * self.SCALE)
                t = time.time()

            l, r = self.read()
            if l >= targetL:
                self.write_left(0)
            if r >= targetR:
                self.write_right(0)

    def rotate(self, angle: float):
        """
        Rotate the robot by an angle (in rotations)
        """
        if angle < 0:
            self.flipR = not self.flipR
            self.move_forward(-angle)
            self.flipR = not self.flipR
        else:
            self.flipL = not self.flipL
            self.move_forward(angle)
            self.flipL = not self.flipL

    def gradual_rotate(self, right: bool, dist: float = 10):

        """
        Move the robot forward by a distance dist (in rotations)
        """
        diff_factor = 1.5
        speed = 50

        self.BP.offset_motor_encoder(
            self.motorL, self.BP.get_motor_encoder(self.motorL)
        )
        self.BP.offset_motor_encoder(
            self.motorR, self.BP.get_motor_encoder(self.motorR)
        )

        if right:
            targetL = 360 * dist * diff_factor
            targetR = 360 * dist
            self.write_left(speed * self.SCALE * diff_factor)
            self.write_right(speed * self.SCALE)
        else:
            targetL = 360 * dist
            targetR = 360 * dist * diff_factor
            self.write_left(speed * self.SCALE)
            self.write_right(speed * self.SCALE * diff_factor)

        l, r = self.read()
        t = time.time()
        while l < targetL or r < targetR:
            if l < targetL and r < targetR and time.time() - t > 0.4:
                ratio = (l - r) / 10
                print(ratio)
                self.write_left((speed - ratio) * self.SCALE)
                self.write_right((speed + ratio) * self.SCALE)
                t = time.time()

            l, r = self.read()
            if l >= targetL:
                self.write_left(0)
            if r >= targetR:
                self.write_right(0)

    def lane_change(self):
        self.gradual_rotate(True)
        self.gradual_rotate(False)
