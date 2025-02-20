import math

def rescale(x, y):
    return (x * 3 + 10, 750 - (y * 3 + 10))


def draw_line(x0: float, y0: float, x1: float, y1: float):
    x0, y0 = rescale(x0, y0)
    x1, y1 = rescale(x1, y1)
    print(f"drawLine: ({x0}, {y0}, {x1}, {y1})")


def draw_particle_with_dir(x: float, y: float, theta: float):  # x,y,theta
    x, y = rescale(x, y)
    print(f"drawLine: ({x}, {y}, {x+10*math.cos(theta)}, {y+10*math.sin(theta)})")
    print(f"drawLine: ({x}, {y}, {x+3*math.cos(theta+math.pi/2)}, {y+3*math.sin(theta+math.pi/2)})")    

def draw_particles(particles: list[tuple[float, float, float]]):  # x,y,theta
    particles = [(*rescale(x, y), theta) for (x, y, theta) in particles]
    print(f"drawParticles: {particles}")
def draw_cross(x: float, y: float, size: int = 5):
    x, y = rescale(x, y)
    print(f"drawLine: ({x-size}, {y-size}, {x+size}, {y+size})")
    print(f"drawLine: ({x-size}, {y+size}, {x+size}, {y-size})")