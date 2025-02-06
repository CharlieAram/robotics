from dataclasses import dataclass, field
import math
from random import gauss
from time import sleep
import brickpi3

def rescale(x,y):
    return (x*10 + 100, y*10 + 100)

def draw_line(x0: float, y0: float, x1: float, y1: float):
    x0,y0 = rescale(x0,y0)
    x1,y1 = rescale(x1,y1)
    print(f"drawLine: ({x0}, {y0}, {x1}, {y1})")

def draw_particles(particles: list[tuple[float, float, float]]): # x,y,theta
    particles = [(*rescale(x,y),theta) for (x,y,theta) in particles]
    print(f"drawParticles: {particles}")

def draw_particle(x: float, y: float, theta: float):
    x,y = rescale(x,y)
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


@dataclass
class weightedPosition:
    pos: Position
    weight: float

    def move_forward(self, D: float):
        self.pos.move_forward(D)

    def rotate(self, angle: float):
        self.pos.rotate(angle)


@dataclass
class ParticleCloud:
    particles: list[weightedPosition] = field(default_factory=list)

    def __iter__(self):
        return iter(self.particles)


class Robot:
    def __init__(self, num_points: int, sigma: float, verbose=False):
        self.BP = brickpi3.BrickPi3()

        # Initialize the robot at the center of the world
        self.sigma = sigma
        self.verbose = verbose
        self.motorR = self.BP.PORT_B # right motor
        self.motorL = self.BP.PORT_C # left motor
        self.speed = 170 # range is -255 to 255, make lower if bot it too fast
        self.ROTS_FWD = 4.244 * (38/42.5) * 1.12
        self.particle_cloud = ParticleCloud(
            [
                weightedPosition(pos=Position(0.0, 0.0, 0.0), weight=1.0 / num_points)
                for _ in range(num_points)
            ]
        )

    # Call when we move the robot forward
    def move_forward(self, D):
        
        self.BP.set_motor_position_relative(self.motorL, (360 * self.ROTS_FWD) * D)
        self.BP.set_motor_position_relative(self.motorR, -(360 * self.ROTS_FWD) * D)
        for particle in self.particle_cloud:
            epsilon = gauss(0, self.sigma)
            particle.rotate(epsilon)
            particle.move_forward(D)
        self.draw_if_verbose()

    # Call when we rotate the robot at each corner
    def rotate(self, angle):
        for particle in self.particle_cloud:
            epsilon = gauss(0, self.sigma)
            particle.rotate(angle + epsilon)
        self.draw_if_verbose()
    
    def draw_if_verbose(self):
        if self.verbose:
            draw_particles([(p.pos.x, p.pos.y, p.pos.theta) for p in self.particle_cloud])

if __name__ == "__main__":
    robot = Robot(100, 0.02, verbose=True)
    
    corners = [(0,0),(40,0),(40,40),(0,40),(0,0)]
    
    for a,b in zip(corners,corners[1:]):
        draw_line(*a,*b)
    
    for _ in range(4):
        for _ in range(4):
            robot.move_forward(10)
            sleep(1)
        robot.rotate(-math.pi / 2)
        sleep(1)
