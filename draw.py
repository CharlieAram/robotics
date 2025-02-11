def draw_line(x0: float, y0: float, x1: float, y1: float):
    print(f"drawLine: ({x0}, {y0}, {x1}, {y1})")


def draw_particles(particles: list[tuple[float, float, float]]):  # x,y,theta
    print(f"drawParticles: {particles}")


def draw_particle(x: float, y: float, theta: float):
    print(f"drawParticles: [({x}, {y}, {theta})]")
