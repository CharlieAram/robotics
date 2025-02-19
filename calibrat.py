from probalistic_motion import Robot

from math import pi as PI

robot = Robot(100, 0, False)
print(robot.driver.read_sensor())
print("Hello")
robot.move_forward(10)
print("goodbye")
print(robot.driver.read_sensor())