from probalistic_motion import Robot
from mcl import NormRobot
from math import pi as PI

robot = NormRobot(100, 0, False)
print(robot.sensor_reading())
print("Hello")
robot.move_forward(10)
print("goodbye")
print(robot.sensor_reading())