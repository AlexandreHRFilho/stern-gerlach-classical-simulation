# Classical Stern-Gerlach Simulation

Python simulation of the Stern-Gerlach experiment using a classical description of the magnetic moment.

The goal is to observe the pattern predicted by classical physics and later compare it with the quantum description.

## Installation

This project uses `uv`.

```bash
uv sync
```

## Run

From the project root:

```bash
uv run python src/stern_gerlach_classico/simulacao.py
```

## Main Parameters

The main parameters are defined inside the `main()` function.

Magnetic Field
magnetic_field = MagneticField(
    start=[0.0, -0.005, -0.005],
    size=[0.035, 0.01, 0.01],
    B0=0.1,
    gradient=1000.0
)
start: position where the magnetic-field region begins, given as [x, y, z].
size: physical dimensions of the magnetic-field region along [x, y, z].
B0: reference magnetic-field strength, in tesla.
gradient: rate at which the magnetic field changes with position, in T/m.

For the values above, the magnetic-field region extends from:

x: 0 to 0.035 m
y: -0.005 to +0.005 m
z: -0.005 to +0.005 m

The field used in the simulation is position-dependent:

[
B_x=-\frac{G}{2}x
]

[
B_y=-\frac{G}{2}y
]

[
B_z=B_0+Gz
]

where (G) is the magnetic-field gradient.

Therefore, B0 sets the reference value of the field, while gradient determines how strongly the field varies across space. This spatial variation is what produces a net force on the magnetic moment.
### Screen

```python
screen = [0.20, 0.05, 0.05]
```

The first value defines the screen position along the \(x\)-axis:

```text
x = 0.20 m
```

This means the screen is placed 20 cm from the initial emission point of the beam. The impact position of each particle is recorded when it reaches this plane.

### Beam

```python
beam = Beam(
    number_particles=1000,
    position=[0.0, 0.0, 0.0],
    velocity=[550.0, 0.0, 0.0],
    mass=1.79e-25,
    magnetic_moment_magnitude=9.274e-24,
    width_y=0.0008,
    width_z=0.00003
)
```

* `number_particles`: number of simulated particles
* `position`: center of the initial beam
* `velocity`: initial velocity
* `mass`: particle mass
* `magnetic_moment_magnitude`: magnetic moment magnitude
* `width_y`: beam width along \(y\)
* `width_z`: beam width along \(z\)

Each particle is emitted from a random initial position inside the beam opening.

## Output

The simulation calculates the motion of each particle until it reaches the screen.

It displays:

* number of emitted particles
* hits, misses, and timeouts
* impact distribution
* 3D plot of the impact points

## Technologies

* Python
* NumPy
* Matplotlib
* uv
