from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from random import gauss
from time import sleep
import os

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
def rescale(x, y):
    return (x * 10 + 100, y * 10 + 100)


def draw_line(x0: float, y0: float, x1: float, y1: float):
    x0, y0 = rescale(x0, y0)
    x1, y1 = rescale(x1, y1)
    print(f"drawLine: ({x0}, {y0}, {x1}, {y1})")


def draw_particles(particles: list[tuple[float, float, float]]):  # x,y,theta
    particles = [(*rescale(x, y), theta) for (x, y, theta) in particles]
    if VERBOSE:
        print(f"drawParticles: {particles}")


@dataclass
class Position:
    x: float
    y: float
    theta: float

    def move_forward(self, D: float):
        self.x += math.cos(self.theta) * D
        self.y += math.sin(self.theta) * D

    def rotate(self, angle: float):
        self.theta += angle
        self.theta = self.normalise(self.theta)

    def __truediv__(self, other):
        return Position(self.x / other, self.y / other, self.normalise(self.theta / other))

    def __mul__(self, other):
        return Position(self.x * other, self.y * other, self.normalise(self.theta * other))

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.normalise(self.theta + other.theta))
    
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
    

def motion(f: Callable[Concatenate["Robot", P], T]) -> Callable[Concatenate["Robot", P], T]:
    def wrapper(self: "Robot", *args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return f(self, *args, **kwargs)
        finally:
            self.update()
    return wrapper


class Robot:
    def __init__(self, num_points: int, sigma: float, verbose=False):
        # Initialize the robot at the center of the world
        self.sigma = sigma
        self.verbose = verbose
        self.motorR = brickpi3.BrickPi3.PORT_B # right motor
        self.motorL = brickpi3.BrickPi3.PORT_C # left motor
        self.speed = 2
        self.FWD_SCALING = (4.244 * (38 / 42.5) * 1.12 * 1/40) / 11 # IDK Chief
        self.TURN_SCALING = (1.1 * 2/math.pi) * SCALE
        self.driver = MotorDriver(self.motorL, self.motorR, self.speed)
        self.driver.flipR = True
        self.particle_cloud = ParticleCloud(
            [
                WeightedPosition(pos=Position(0.0, 0.0, 0.0), weight=1.0 / num_points)
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
    
    def navigateToWaypoint(self, x, y, i=1):
        (robot_x, robot_y, robot_theta) = self.getMeanPos()
        print(f"robot_x: {robot_x}, robot_y: {robot_y}, robot_theta: {robot_theta}")
        print(f"target x: {x}, target y: {y}")
        r = (math.sqrt((x - robot_x) ** 2 + (y - robot_y) ** 2)) / i
        theta = math.atan2(y - robot_y, x - robot_x) - robot_theta
        print(f"{r=}, {theta=}")
        # Normalize theta to be within the range [-pi, pi]
        theta = (theta + math.pi) % (2 * math.pi) - math.pi
        print(f"theta: {theta}, r: {r}")

        self.rotate(theta)
        for _ in range(i):
            self.move_forward(r)
            sleep(0.5)
        (robot_x, robot_y, robot_theta) = self.getMeanPos()
        print(f"robot_x: {robot_x}, robot_y: {robot_y}, robot_theta: {robot_theta}")


    # Call when we move the robot forward
    @motion
    def move_forward(self, D):
        self.driver.move_forward(D * self.FWD_SCALING)
        for particle in self.particle_cloud:
            epsilon = gauss(0, self.sigma)
            particle.rotate(epsilon)
            particle.move_forward(D)
        print("mean pos", self.getMeanPos())

    # Call when we rotate the robot at each corner
    @motion
    def rotate(self, angle):
        self.driver.rotate(angle * self.TURN_SCALING)
        for particle in self.particle_cloud:
            epsilon = gauss(0, self.sigma)
            particle.rotate(angle + epsilon)
        print("rot mean pos", self.getMeanPos())

    def update(self):
        print("updating")
        if self.verbose:
            draw_particles(
                [(p.pos.x, p.pos.y, p.pos.theta) for p in self.particle_cloud]
            )


if __name__ == "__main__":
    # robot = Robot(100, 0.02, verbose=True)
    
    # corners = [(0,0),(40,0),(40,40),(0,40),(0,0)]
    
    # for a,b in zip(corners,corners[1:]):
    #     draw_line(*a,*b)
    
    # for _ in range(4):
    #     for _ in range(4):
    #         robot.move_forward(10)
    #         sleep(1)
    #     robot.rotate((math.pi/2))
    #     sleep(1)
    # robot = Robot(100, 0.02, verbose=True)
    # robot.update()
    # robot.navigateToWaypoint(5, 0, 3)
    # robot.navigateToWaypoint(5, 5, 3)
    # robot.navigateToWaypoint(0, 5, 3)
    # robot.navigateToWaypoint(0, 0, 3)
    robot = Robot(100, 0.02, verbose=True)
    robot.update()
    
    while True:
        try:
            x = float(input("Enter x coordinate: "))
            y = float(input("Enter y coordinate: "))
            robot.navigateToWaypoint(x, y, 4)
        except ValueError:
            print("Please enter valid numbers for coordinates")
