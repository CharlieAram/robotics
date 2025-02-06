1. When placed facing and perpendicular to a smooth surface such as a wall, what are the minimum
and maximum depths that the sensor can reliably measure?
5cm and 185cm

2. Move the sonar so that it faces the wall at a non-orthogonal incidence angle. What is the maximum angular deviation from perpendicular to the wall at which it will still give sensible readings?
45 degrees

3. Do your sonar depth measurements have any systematic (non-zero mean) errors? To test this, set
up the sensor at a range of hand-measured depths (20cm, 40cm, 60cm, 80cm, 100cm) from a wall
and record depth readings. Are they consistently above or below what they should be?
20cm - 22
40cm - 43
60cm - 63
80cm - 85
100cm - 103


4. What is the the accuracy of the sonar sensor and does it depend on depth? At each of two chosen
hand-measured depths (40cm and 100cm), make 10 separate depth measurements (each time
picking up and replacing the sensor) and record the values. Do you observe the same level of
scatter in each case?
100cm - 103, 103, 103, 103, 103, 103, 103, 103, 103, 103
40cm - 42, 42, 42, 42, 42, 42, 42, 42, 42, 42
Accuracy high, no scatter, doesn't depend on depts

5. In a range of general conditions for robot navigation, what fraction of the time do you think your
sonar gives garbage readings very far from ground truth?
Around 10% of the time the sonar gives garbage readings, particularly when:
- The surface is at too steep an angle (>45 degrees)
- The surface is too close (<5cm) or too far (>185cm) 
- The surface is very uneven or has gaps
- There are multiple reflective surfaces in range
- The sensor is moving too quickly
