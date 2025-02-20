from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from random import gauss
from time import sleep
import os
import sys
from draw import draw_line, draw_particles

VISUALISATION = not bool(len(sys.argv) > 1)

if "pi" in os.path.expanduser("~").split(os.path.sep):
    import brickpi3
    from motor_driver import MotorDriver
else:

    class SelfReturningMock:
        BrickPi3: "SelfReturningMock"
        flipR: bool

        def __init__(self, *args, **kwargs) -> None:
            pass

        def __getattribute__(self, name):
            return self

        def __getattr__(self, name):
            return self

        def __call__(self, *args, **kwargs):
            return self

    SelfReturningMock.BrickPi3 = SelfReturningMock()
    MotorDriver = SelfReturningMock
    brickpi3 = SelfReturningMock

import sys

SCALE = eval(" ".join(sys.argv[1:])) if len(sys.argv) > 1 else 1

VERBOSE = False

OFS = 1.5

@dataclass
class Position:
    x: float
    y: float
    theta: float

    def move_forward(self, D: float):
        self.x += math.cos(self.theta) * D
        self.y -= math.sin(self.theta) * D # Unflip axis
        assert abs(self.x) < 400 and abs(self.y) < 400, f"{self.x=}, {self.y=}"

    def rotate(self, angle: float):
        self.theta += angle
        self.theta = self.normalise(self.theta)

    def __truediv__(self, other):
        return Position(
            self.x / other, self.y / other, self.normalise(self.theta / other)
        )

    def __mul__(self, other):
        return Position(
            self.x * other, self.y * other, self.normalise(self.theta * other)
        )

    def __add__(self, other):
        return Position(
            self.x + other.x, self.y + other.y, self.normalise(self.theta + other.theta)
        )

    @staticmethod
    def normalise(theta: float):
        return (theta + math.pi) % (2 * math.pi) - math.pi


@dataclass
class WeightedPosition:
    pos: Position
    weight: float

    def move_forward(self, D: float):
        self.pos.move_forward(D)

    def rotate(self, angle: float):
        self.pos.rotate(angle)

    def clone_with_weight(self, weight: float):
        return WeightedPosition(pos=replace(self.pos), weight=weight)


@dataclass
class ParticleCloud:
    particles: list[WeightedPosition] = field(default_factory=list)

    def __iter__(self):
        return iter(self.particles)


from typing import TYPE_CHECKING, Callable, TypeVar

if TYPE_CHECKING:
    from typing import ParamSpec, Concatenate

    P = ParamSpec("P")
    T = TypeVar("T")


def motion(
    f: Callable[Concatenate["Robot", P], T],
) -> Callable[Concatenate["Robot", P], T]:
    def wrapper(self: "Robot", *args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return f(self, *args, **kwargs)
        finally:
            self.update()

    return wrapper


class Robot:
    def __init__(self, num_points: int, start_x: float = 0.0, start_y: float = 0.0, start_theta: float = 0.0, VIS=False):
        # Initialize the robot at the center of the world
        self.e = 0.26 # Fwd dist uncertainty [measured]
        self.f = 1.5 * math.pi/180 # Fwd rot uncertainty
        self.g = 2 * math.pi/180 # pure rotation uncertainty
        self.VIS = VIS
        self.motorR = brickpi3.BrickPi3.PORT_B  # right motor
        self.motorL = brickpi3.BrickPi3.PORT_C  # left motor
        self.speed = 2
        self.FWD_SCALING = 4.244 * (38 / 42.5) * 1.12 * 1 / 40  # IDK Chief
        self.TURN_SCALING = 1.1 * 2 / math.pi
        self.driver = MotorDriver(self.motorL, self.motorR, self.speed)
        self.driver.flipR = True
        self.particle_cloud = ParticleCloud(
            [
                WeightedPosition(pos=Position(start_x, start_y, start_theta), weight=1.0 / num_points)
                for _ in range(num_points)
            ]
        )

    def getMeanPos(self):
        pos = sum(
            [
                particle.pos * particle.weight
                for particle in self.particle_cloud.particles
            ],
            Position(0, 0, 0),
        )
        return pos.x, pos.y, pos.theta

    def getTargeting(self, x: float, y: float):
        robot_x, robot_y, robot_theta = self.getMeanPos()
        print(f"robot_x: {robot_x}, robot_y: {robot_y}, robot_theta: {robot_theta}")
        print(f"target x: {x}, target y: {y}")
        r = math.sqrt((x - robot_x) ** 2 + (y - robot_y) ** 2)
        theta = -math.atan2(y - robot_y, x - robot_x) - robot_theta
        # Normalize theta to be within the range [-pi, pi]
        theta = (theta + math.pi) % (2 * math.pi) - math.pi
        return r, theta

    def navigateToWaypoint(self, x, y, i=20):
        r, theta = self.getTargeting(x, y)
        print(f"{r=}, {theta=}")
        self.rotate(theta)

        # Assume that we are at the right angle now
        r, theta = self.getTargeting(x, y)
        if abs(theta) > 10 * 3.14159/180:
            print(f"WARNING: {theta} angle error!")
        if r > i:
            self.move_forward(i - OFS)
            sleep(0.5)
            self.navigateToWaypoint(x, y, i)
            return

        self.move_forward(r - OFS)
        sleep(0.5)
        (robot_x, robot_y, robot_theta) = self.getMeanPos()
        print(f"TARGET REACHED, robot_x: {robot_x}, robot_y: {robot_y}, robot_theta: {robot_theta}")

    # Call when we move the robot forward
    @motion
    def move_forward(self, D):
        print(f"move_forward: {D}")
        self.driver.move_forward(D * self.FWD_SCALING)
        for particle in self.particle_cloud:
            e = gauss(0, self.e)
            f = gauss(0, self.f)
            particle.move_forward(D + e)
            particle.rotate(f)
        print("mean pos", self.getMeanPos())

    # Call when we rotate the robot at each corner
    @motion
    def rotate(self, angle):
        self.driver.rotate(angle * self.TURN_SCALING)
        for particle in self.particle_cloud:
            g = gauss(0, self.g)
            particle.rotate(angle + g)
        print("rot mean pos", self.getMeanPos())

    def update(self):
        print("updating")
        if self.VIS:
            draw_particles(
                [(p.pos.x, p.pos.y, p.pos.theta) for p in self.particle_cloud]
            )


if __name__ == "__main__":
    if VISUALISATION:
        robot = Robot(100, VIS=True)

        corners = [(0, 0), (40, 0), (40, 40), (0, 40), (0, 0)]

        for a, b in zip(corners, corners[1:]):
            draw_line(*a, *b)

        for _ in range(4):
            robot.move_forward(40)
            sleep(1)
            robot.rotate((math.pi / 2))
            sleep(1)
    else:
        robot = Robot(100, VIS=False)
        robot.update()

        while True:
            try:
                x = float(input("Enter x coordinate: "))
                y = float(input("Enter y coordinate: "))
                robot.navigateToWaypoint(x, y)
            except ValueError:
                print("Please enter valid numbers for coordinates")
