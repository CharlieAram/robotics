from dataclasses import dataclass, field
import math
from random import gauss
from draw import draw_particles

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
        # Initialize the robot at the center of the world
        self.sigma = sigma
        self.verbose = verbose
        self.particle_cloud = ParticleCloud(
            [
                weightedPosition(pos=Position(0.0, 0.0, 0.0), weight=1.0 / num_points)
                for _ in range(num_points)
            ]
        )

    # Call when we move the robot forward
    def move_forward(self, D):
        for particle in self.particle_cloud.particles:
            epsilon = gauss(0, self.sigma)
            particle.rotate(epsilon)
            particle.move_forward(D)
        self.draw_if_verbose()

    # Call when we rotate the robot at each corner
    def rotate(self, angle):
        for particle in self.particle_cloud.particles:
            epsilon = gauss(0, self.sigma)
            particle.rotate(angle + epsilon)
        self.draw_if_verbose()
    
    def draw_if_verbose(self):
        if self.verbose:
            draw_particles([(p.pos.x, p.pos.y, p.pos.theta) for p in self.particle_cloud])

if __name__ == "__main__":
    robot = Robot(20, 0.1, verbose=True)
    robot.move_forward(1)
    robot.rotate(math.pi / 2)
    robot.move_forward(1)
    robot.rotate(math.pi / 2)
    robot.move_forward(1)
    robot.rotate(math.pi / 2)
    robot.move_forward(1)
    robot.rotate(math.pi / 2)
