from dataclasses import dataclass, field, replace
import math
from random import gauss
from time import sleep
from typing import Callable
import brickpi3
from motor_driver import MotorDriver

def rescale(x, y):
    return (x * 10 + 100, y * 10 + 100)


def draw_line(x0: float, y0: float, x1: float, y1: float):
    x0, y0 = rescale(x0, y0)
    x1, y1 = rescale(x1, y1)
    print(f"drawLine: ({x0}, {y0}, {x1}, {y1})")


def draw_particles(particles: list[tuple[float, float, float]]):  # x,y,theta
    particles = [(*rescale(x, y), theta) for (x, y, theta) in particles]
    print(f"drawParticles: {particles}")


def draw_particle(x: float, y: float, theta: float):
    x, y = rescale(x, y)
    print(f"drawParticles: [({x}, {y}, {theta})]")


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
        self.ROTS_FWD = 4.244 * (38 / 42.5) * 1.12 * 1/40 # IDK Chief
        self.ROTS_TURN = 1.1 * 2/math.pi
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
    
    @motion
    def navigateToWaypoint(self, x, y, i=1):
        (robot_x, robot_y, robot_theta) = self.getMeanPos()
        print(f"robot_x: {robot_x}, robot_y: {robot_y}, robot_theta: {robot_theta}")
        r = (math.sqrt((x - robot_x) ** 2 + (y - robot_y) ** 2)) / i
        theta = math.atan2(y - robot_y, x - robot_x) - robot_theta
        print(f"theta: {theta}, r: {r}")

        self.driver.rotate(theta)
        for particle in self.particle_cloud:
            epsilon = gauss(0, self.sigma)
            particle.rotate(theta + epsilon)
        for _ in range(i):
            self.update()
            self.driver.move_forward(r)
            for particle in self.particle_cloud:
                epsilon = gauss(0, self.sigma) 
                particle.rotate(epsilon)
                particle.move_forward(r)
            sleep(0.5)


    # Call when we move the robot forward
    @motion
    def move_forward(self, D):
        print("mean pos", self.getMeanPos())
        self.BP.set_motor_position_relative(self.motorL, (360 * self.ROTS_FWD * D))
        self.BP.set_motor_position_relative(self.motorR, -(360 * self.ROTS_FWD * D))
        for particle in self.particle_cloud:
            epsilon = gauss(0, self.sigma)
            particle.rotate(epsilon)
            particle.move_forward(D)

    # Call when we rotate the robot at each corner
    @motion
    def rotate(self, angle):
        print("rot mean pos", self.getMeanPos())
        self.BP.set_motor_position_relative(self.motorL, (360 * self.ROTS_TURN) * angle)
        self.BP.set_motor_position_relative(self.motorR, (360 * self.ROTS_TURN) * angle)
        for particle in self.particle_cloud:
            epsilon = gauss(0, self.sigma)
            particle.rotate(angle + epsilon)

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
        robot = Robot(100, 0.02, verbose=True)
        robot.update()
        robot.navigateToWaypoint(10, 0, 3)
        robot.navigateToWaypoint(10, 10, 3)
        robot.navigateToWaypoint(0, 10, 3)
        robot.navigateToWaypoint(0, 0, 3)
    except KeyboardInterrupt:
        robot.BP.reset_all()
        print("Tom is a gimp")
