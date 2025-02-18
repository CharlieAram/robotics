import math
from time import sleep
from typing import override
from draw import draw_line
from probalistic_motion import Robot
from random import choices
from copy import deepcopy
import brickpi3
import sys


VISUALISATION = not bool(len(sys.argv) > 1)


# Start and end point of each wall
WALLS = {
    "OA": [(0, 0), (0, 168)],
    "AB": [(0, 168), (84, 168)],
    "BC": [(84, 168), (84, 126)],
    "CD": [(84, 126), (84, 210)],
    "DE": [(84, 210), (168, 210)],
    "EF": [(168, 210), (168, 84)],
    "FG": [(168, 84), (210, 84)],
    "GH": [(210, 84), (210, 0)],
    "HO": [(210, 0), (0, 0)],
}

SD = 2.5  # Standard deviation of the sonar sensor


def distance_to_wall(x, y, theta, wall: str):
    # Get the start and end points of the wall
    (ax, ay), (bx, by) = WALLS[wall]

    c, s = math.cos(theta), math.sin(theta)

    dist = ((by - ay) * (ax - x) - (bx - ax) * (ay - y)) / (
        (by - ay) * c - (bx - ax) * s
    )

    int_x = x + dist * c
    int_y = y + dist * s

    # Check if the intersection point is within the wall
    if (int_x - ax) * (int_x - bx) > 0 or (int_y - ay) * (int_y - by) > 0:
        return float("inf")

    return dist


# x, y, theta: current position and orientation of the robot
# z is the sonar measurement
def calculate_likelihood(x, y, theta, z):
    # Find which wall the sonar beam would hit to then use in calculation
    dist, _ = min([(distance_to_wall(x, y, theta, wall), wall) for wall in WALLS])

    # beta = math.acos(
    #     (math.cos(theta) * (ay - by) + math.sin(theta) * (bx - ax)) /
    #     (math.sqrt((ay - by)**2 + (bx - ax)**2))
    # )

    # TODO: Need to add reasonable constant
    return math.exp(-((z - dist) ** 2) / (2 * SD**2))


class NormRobot(Robot):
    def sensor_reading(self) -> float:
        return self.driver.read_sensor()

    def normalise_probs(self, x, y, theta, z):
        likelihoods = [
            calculate_likelihood(x, y, theta, z) for _ in self.particle_cloud
        ]
        total = sum(likelihoods)
        likelihoods = [l / total for l in likelihoods]

        self.particle_cloud.particles = [
            p.clone_with_weight(prob)
            for p, prob in choices(
                zip(self.particle_cloud.particles, likelihoods),
                likelihoods,
                k=len(self.particle_cloud.particles),
            )
        ]

    @override
    def update(self):
        self.normalise_probs(*self.getMeanPos(), self.sensor_reading())
        super().update()


if __name__ == "__main__":
    if VISUALISATION:
        robot = NormRobot(100, 0.02, VIS=True)

        corners = [(0, 0), (40, 0), (40, 40), (0, 40), (0, 0)]

        for a, b in zip(corners, corners[1:]):
            draw_line(*a, *b)

        for _ in range(4):
            robot.move_forward(40)
            sleep(1)
            robot.rotate((math.pi / 2))
            sleep(1)
    else:
        robot = NormRobot(100, 0.02, VIS=False)
        robot.update()

        while True:
            try:
                x = float(input("Enter x coordinate: "))
                y = float(input("Enter y coordinate: "))
                robot.navigateToWaypoint(x, y, 10)
            except ValueError:
                print("Please enter valid numbers for coordinates")
