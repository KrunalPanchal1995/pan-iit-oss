# Roadmap: the path to the opencrashsim Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Add an occupant and a belt

**You will learn:** Two-mass models: why the occupant's deceleration is not the car's, and how belt slack and stiffness shape it.

**You will build:** A second mass of 75 kg connected to the car by a belt with 30 mm slack, 80 kN/m stiffness and 1500 N s/m damping, with the belt reaction acting back on the car.

**Checkpoint (not met by the shipped code):** For Fp = 200 kN and Lc = 0.80 m at 56 km/h the occupant's peak deceleration is between 27 and 31 g, higher than the car's 20.4 g (the shipped lesson has no occupant at all).

**Difficulty:** intermediate

## Session 5: A staged crumple profile

**You will learn:** Why a single plateau cannot serve both low-speed and high-speed crashes, and how a soft stage followed by a stiff stage can.

**You will build:** A force law with two plateaus and a transition length, swept over 40, 56 and 64 km/h.

**Checkpoint (not met by the shipped code):** Peak at most 18 g at 40 km/h and at most 33 g at 64 km/h with no bottoming out inside 0.70 m. No single plateau does it: 176 kN holds 40 km/h to 17.9 g but bottoms out at 64 km/h (stop 0.746 m), and 235 kN reaches 64 km/h but gives 24 g at 40 km/h.

**Difficulty:** intermediate

## Session 6: Rebound and restitution

**You will learn:** What happens when the structure springs back: coefficient of restitution and unloading curves.

**You will build:** An unloading path for the force curve so that the car can leave the barrier.

**Checkpoint (not met by the shipped code):** With a coefficient of restitution of 0.1 the car leaves at 0.1 of the impact speed, 1 percent of the initial kinetic energy returns as rebound kinetic energy, and the energy balance still closes to 1e-6 (the shipped code ends at rest).

**Difficulty:** intermediate

## Session 7: Off-centre crash with yaw

**You will learn:** Rotation in a crash: moment of inertia, angular momentum and why an offset impact spins the car.

**You will build:** A 2D rigid car with yaw inertia 1500 kg m^2 hitting a barrier 0.5 m off the centreline with the same plateau force law.

**Checkpoint (not met by the shipped code):** Linear momentum change equals the impulse and the total energy (translation, rotation and crush work) closes to 1e-6, with a non-zero yaw rate after contact.

**Difficulty:** advanced

## Session 8: Reproduce the Target animation

**You will learn:** Animating a simulation: frames, live traces and an energy bar that stays in step with the physics.

**You will build:** A side-by-side GIF of a bottoming-out design and a tuned design, each with a car picture, a live deceleration trace and an energy split.

**Checkpoint (not met by the shipped code):** A GIF under 3 MB with at most 60 frames whose final trace values and energy bars equal your simulation to 1e-6.

**Difficulty:** advanced

## The final step

Combine the milestones: a car with an occupant and a belt, a staged crumple profile that works across speeds, and a clean animation with a live deceleration trace and an energy bar. If your result looks like the Target animation, open a pull request and tell us how you did it.
