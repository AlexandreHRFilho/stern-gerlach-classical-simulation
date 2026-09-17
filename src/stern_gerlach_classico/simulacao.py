import numpy as np
import matplotlib.pyplot as plt


class Particle:
    def __init__(self, position, velocity, mass, magnetic_moment_magnitude):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.mass = float(mass)
        self.magnetic_moment_magnitude = float(magnetic_moment_magnitude)

        self.theta = np.random.uniform(0.0, np.pi)

        mu = self.magnetic_moment_magnitude

        self.magnetic_moment = np.array([
            mu * np.sin(self.theta),
            0.0,
            mu * np.cos(self.theta)
        ])


class MagneticField:
    def __init__(self, start, size, B0, gradient):
        self.start = np.array(start, dtype=float)
        self.size = np.array(size, dtype=float)
        self.end = self.start + self.size
        self.B0 = float(B0)
        self.gradient = float(gradient)

    def field_formula(self, position):
        x, y, z = position
        G = self.gradient

        Bx = -(G / 2) * x
        By = -(G / 2) * y
        Bz = self.B0 + G * z

        return np.array([Bx, By, Bz])

    def field_at(self, position):
        position = np.array(position, dtype=float)

        if np.any(position < self.start) or np.any(position > self.end):
            return np.zeros(3)

        return self.field_formula(position)

    def force_on(self, particle, h=1e-6):
        position = particle.position
        mu = particle.magnetic_moment

        if np.any(position < self.start) or np.any(position > self.end):
            return np.zeros(3)

        force = np.zeros(3)

        for axis in range(3):
            displacement = np.zeros(3)
            displacement[axis] = h

            B_plus = self.field_formula(position + displacement)
            B_minus = self.field_formula(position - displacement)

            force[axis] = (
                np.dot(mu, B_plus) - np.dot(mu, B_minus)
            ) / (2 * h)

        return force


class Beam:
    def __init__(
        self,
        number_particles,
        position,
        velocity,
        mass,
        magnetic_moment_magnitude,
        width_y=0.0008,
        width_z=0.00003
    ):
        self.number_particles = int(number_particles)
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.mass = float(mass)
        self.magnetic_moment_magnitude = float(magnetic_moment_magnitude)
        self.width_y = float(width_y)
        self.width_z = float(width_z)
    def emit_particle(self):
        position = self.position.copy()

        position[1] += np.random.uniform(
            -self.width_y / 2,
            self.width_y / 2
        )

        position[2] += np.random.uniform(
            -self.width_z / 2,
            self.width_z / 2
        )

        return Particle(
            position,
            self.velocity.copy(),
            self.mass,
            self.magnetic_moment_magnitude
        )


class SternGerlachExperiment:
    def __init__(self, magnetic_field, screen):
        self.magnetic_field = magnetic_field
        self.screen = np.array(screen, dtype=float)

    def step(self, particle, dt):
        force = self.magnetic_field.force_on(particle)
        acceleration = force / particle.mass

        particle.velocity += acceleration * dt
        particle.position += particle.velocity * dt

    def simulate_particle(self, particle, dt, max_time=0.01):
        time = 0.0
        screen_x = self.screen[0]

        while time < max_time:
            previous_position = particle.position.copy()

            self.step(particle, dt)
            time += dt

            current_position = particle.position.copy()

            crossed_screen = (
                previous_position[0] < screen_x
                and current_position[0] >= screen_x
            )

            if crossed_screen:
                alpha = (
                    (screen_x - previous_position[0])
                    / (current_position[0] - previous_position[0])
                )

                impact = previous_position + alpha * (
                    current_position - previous_position
                )

                inside_y = abs(impact[1]) <= self.screen[1]
                inside_z = abs(impact[2]) <= self.screen[2]

                status = "hit" if inside_y and inside_z else "miss"

                return {
                    "status": status,
                    "impact": impact,
                    "time": time,
                    "theta": particle.theta,
                    "magnetic_moment": particle.magnetic_moment.copy()
                }

        return {
            "status": "timeout",
            "impact": None,
            "time": time,
            "theta": particle.theta,
            "magnetic_moment": particle.magnetic_moment.copy()
        }

    def simulate(self, beam, dt, max_time=0.01):
        results = []

        for _ in range(beam.number_particles):
            particle = beam.emit_particle()
            result = self.simulate_particle(
                particle,
                dt=dt,
                max_time=max_time
            )
            results.append(result)

        return results


def get_impacts(results):
    impacts = []

    for result in results:
        if result["status"] == "hit":
            impacts.append(result["impact"])

    return np.array(impacts, dtype=float)


def plot_impacts_3d(impacts, screen):
    if len(impacts) == 0:
        print("Nenhuma partícula atingiu a tela.")
        return

    x = impacts[:, 0]
    y = impacts[:, 1]
    z = impacts[:, 2]

    print("\nDISTRIBUIÇÃO NA TELA")
    print("y mínimo:", np.min(y), "m")
    print("y máximo:", np.max(y), "m")
    print("z mínimo:", np.min(z), "m")
    print("z máximo:", np.max(z), "m")
    print("Desvio máximo em y:", np.max(np.abs(y)) * 1000, "mm")
    print("Desvio máximo em z:", np.max(np.abs(z)) * 1000, "mm")

    max_abs_y = np.max(np.abs(y))
    max_abs_z = np.max(np.abs(z))

    visual_y = max(max_abs_y * 1.3, 0.0002)
    visual_z = max(max_abs_z * 1.3, 0.0002)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(x, y, z, s=8)

    y_screen = np.linspace(-visual_y, visual_y, 2)
    z_screen = np.linspace(-visual_z, visual_z, 2)

    Y, Z = np.meshgrid(y_screen, z_screen)
    X = np.full_like(Y, screen[0])

    ax.plot_surface(X, Y, Z, alpha=0.12)

    x_zoom = 0.0005

    ax.set_xlim(screen[0] - x_zoom, screen[0] + x_zoom)
    ax.set_ylim(-visual_y, visual_y)
    ax.set_zlim(-visual_z, visual_z)

    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ax.set_title("Distribuição dos impactos")

    ax.view_init(elev=20, azim=-55)

    plt.show()


def main():
    magnetic_field = MagneticField(
        start=[0.0, -0.005, -0.005],
        size=[0.035, 0.01, 0.01],
        B0=0.1,
        gradient=1000.0
    )

    screen = [0.20, 0.05, 0.05]

    experiment = SternGerlachExperiment(
        magnetic_field=magnetic_field,
        screen=screen
    )

    beam = Beam(
        number_particles=1000,
        position=[0.0, 0.0, 0.0],
        velocity=[550.0, 0.0, 0.0],
        mass=1.79e-25,
        magnetic_moment_magnitude=9.274e-24,
        width_y=0.0008,
        width_z=0.00003
    )

    results = experiment.simulate(
        beam,
        dt=1e-7,
        max_time=0.01
    )
    hits = sum(r["status"] == "hit" for r in results)
    misses = sum(r["status"] == "miss" for r in results)
    timeouts = sum(r["status"] == "timeout" for r in results)

    print("\nFEIXE")
    print("Largura em y:", beam.width_y * 1000, "mm")
    print("Largura em z:", beam.width_z * 1000, "mm")
    print("As partículas são emitidas aleatoriamente dentro dessa abertura.")

    print("\nRESULTADOS")
    print("Partículas emitidas:", len(results))
    print("Hits:", hits)
    print("Misses:", misses)
    print("Timeouts:", timeouts)

    impacts = get_impacts(results)

    print("Pontos registrados:", len(impacts))

    plot_impacts_3d(impacts, screen)


if __name__ == "__main__":
    main()