from probalistic_motion import Robot

from math import pi as PI

robot = Robot(100, 0, False)
print(robot.getMeanPos())
print(robot.driver.read_sensor())
robot.move_forward(10)
print(robot.getMeanPos())
print(robot.driver.read_sensor())