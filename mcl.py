import math
from time import sleep

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import override
else:
    override = lambda x: x
from draw import draw_line, draw_cross
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

SD = 0.5  # Standard deviation of the sonar sensor


def distance_to_wall(x: float, y: float, theta: float, wall: str) -> float:
    # Get the start and end points of the wall
    (ax, ay), (bx, by) = WALLS[wall]

    c, s = math.cos(theta), math.sin(theta)

    dist = ((by - ay) * (ax - x) - (bx - ax) * (ay - y)) / (
        (by - ay) * c - (bx - ax) * s
    )

    int_x = x + dist * c
    int_y = y + dist * s

    # The wall is behind you, you should not be able to sense it
    if dist < 0:
        return float("inf")

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
    return dist, math.exp(-((z - dist) ** 2) / (2 * SD**2))


class NormRobot(Robot):
    def sensor_reading(self) -> float:
        readings = []
        while len(readings) < 10:
            x = self.driver.read_sensor()
            if x is not None:
                readings.append(x)
            sleep(0.01)
        readings.sort()
        print("sensor reading=", readings[4])
        return readings[4]

    def normalise_probs(self, z):
        probs, dists = [], []

        for p in self.particle_cloud:
            dist, prob = calculate_likelihood(p.pos.x, p.pos.y, p.pos.theta, z)
            dists.append(dist)
            probs.append(prob + 0.01) # Baseline 1% error rate

        print("average expected dist", sum(dists) / len(dists))
        total = sum(probs)
        likelihoods = [l / total for l in probs]

        self.particle_cloud.particles = [
            p.clone_with_weight(prob)
            for p, prob in choices(
                list(zip(self.particle_cloud.particles, likelihoods)),
                likelihoods,
                k=len(self.particle_cloud.particles),
            )
        ]
        total_p = sum(p.weight for p in self.particle_cloud.particles)
        assert abs(total_p - 1) < 0.001, f"probs should sum to 1, not {total_p}"

    @override
    def update(self):
        self.normalise_probs(self.sensor_reading())
        super().update()


if __name__ == "__main__":
    if VISUALISATION:
        robot = NormRobot(100, start_x=84, start_y=30, VIS=True)

        waypoints = [
            (84, 30),
            (180, 30),
            (180, 54),
            (138, 54),
            (138, 168),
            (114, 168),
            (114, 84),
            (84, 84),
            (84, 30),
        ]

        for wall in WALLS.values():
            draw_line(wall[0][0], wall[0][1], wall[1][0], wall[1][1])
        for waypoint in waypoints:
            draw_cross(*waypoint)

        start = waypoints[0]
        for a, b in waypoints[1:]:
            draw_line(start[0], start[1], a, b)
            robot.navigateToWaypoint(a, b, 10)
            start = (a, b)
            sleep(3)
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
