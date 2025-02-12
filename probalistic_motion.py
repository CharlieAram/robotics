from dataclasses import dataclass, field, replace
import math
from random import gauss
from time import sleep
from typing import Callable
import brickpi3
from motor_driver import MotorDriver
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

    def __truediv__(self, other):
        return Position(self.x / other, self.y / other, self.theta / other)

    def __mul__(self, other):
        return Position(self.x * other, self.y * other, self.theta * other)

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.theta + other.theta)


@dataclass
class weightedPosition:
    pos: Position
    weight: float

    def move_forward(self, D: float):
        self.pos.move_forward(D)

    def rotate(self, angle: float):
        self.pos.rotate(angle)

    def clone_with_weight(self, weight: float):
        return weightedPosition(pos=replace(self.pos), weight=weight)


@dataclass
class ParticleCloud:
    particles: list[weightedPosition] = field(default_factory=list)

    def __iter__(self):
        return iter(self.particles)


def motion(f: Callable[["Robot"], None]):
    def wrapper(self: "Robot", *args, **kwargs):
        f(self, *args, **kwargs)
        self.update()

    return wrapper


class Robot:
    def __init__(self, num_points: int, sigma: float, verbose=False):
        self.BP = brickpi3.BrickPi3()

        # Initialize the robot at the center of the world
        self.sigma = sigma
        self.verbose = verbose
        self.motorR = self.BP.PORT_B # right motor
        self.motorL = self.BP.PORT_C # left motor
        self.speed = 2
        self.FWD_SCALING = 1
        self.TURN_SCALING = (1.1 * 2/math.pi) * SCALE
        self.driver = MotorDriver(self.motorL, self.motorR, self.speed)
        self.driver.flipR = True
        self.particle_cloud = ParticleCloud(
            [
                weightedPosition(pos=Position(0.0, 0.0, 0.0), weight=1.0 / num_points)
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
        r = (math.sqrt((x - robot_x) ** 2 + (y - robot_y) ** 2)) / i
        theta = math.atan2(y - robot_y, x - robot_x) - robot_theta
        # Normalize theta to be within the range [-pi, pi]
        theta = (theta + math.pi) % (2 * math.pi) - math.pi
        print(f"theta: {theta}, r: {r}")

        self.rotate(theta)
        for _ in range(i):
            self.move_forward(r / i)
            sleep(0.5)


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
    try: 
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
    except KeyboardInterrupt:
        robot.BP.reset_all()
        print("Tom is a gimp")
