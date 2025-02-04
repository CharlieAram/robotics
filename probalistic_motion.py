
from dataclasses import dataclass, field
import math
import numpy as np

@dataclass(slots=True)
class Position:
    x: float
    y: float
    theta: float

    def move_forward(self, D: float):
        self.x += math.cos(self.theta) * D
        self.y += math.sin(self.theta) * D
    
    def rotate(self, angle: float):
        self.theta += angle

@dataclass(slots=True)
class weightedPosition:
    pos: Position
    weight: float

    def move_forward(self, D: float):
        self.pos.move_forward(D)
    
    def rotate(self, angle: float):
        self.pos.rotate(angle)

@dataclass(slots=True)
class ParticleCloud:
    particles: list[weightedPosition] = field(default_factory=list)

class Robot():
    def __init__(self, num_points: int, sigma: float):
        # Initialize the robot at the center of the world
        self.sigma = sigma
        self.particle_cloud = ParticleCloud()
        for _ in range(num_points):
            pos = Position(0.0, 0.0, 0.0)
            weighted_pos = weightedPosition(pos=pos, weight=1.0/num_points)
            self.particle_cloud.particles.add(weighted_pos)

    # Call when we move the robot forward
    def move_forward(self, D):
        for particle in self.particle_cloud.particles:
            epsilon = np.random.normal(0, self.sigma)
            particle.rotate(epsilon)
            particle.move_forward(D)

    # Call when we rotate the robot at each corner
    def rotate(self, angle):
        for particle in self.particle_cloud.particles:
            epsilon = np.random.normal(0, self.sigma)
            particle.rotate(angle + epsilon)
    



if __name__ == "__main__":
    robot = Robot(100, 0.1)
    robot.move_forward(1)
    robot.rotate(math.pi/2)
    robot.move_forward(1)
    robot.rotate(math.pi/2)
    robot.move_forward(1)
    robot.rotate(math.pi/2)
    robot.move_forward(1)
    robot.rotate(math.pi/2)
    print(robot.particle_cloud.particles)
    print("Done")