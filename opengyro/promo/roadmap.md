# Roadmap: the path to the opengyro Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A top that can start exactly vertical

**You will learn:** Why Euler angles are singular at the pole and how a quaternion or rotation matrix avoids it.

**You will build:** The same top integrated with a quaternion for the attitude and the body-frame Euler equations.

**Checkpoint (not met by the shipped code):** A top released exactly vertical (tilt 0) at twice the sleeping limit stays within 0.5 degrees of vertical for 3 s with no NaN (the shipped code returns NaN there).

**Difficulty:** intermediate

## Session 5: Predict the mean precession from the effective potential

**You will learn:** Reducing the top to one-dimensional motion in theta with an effective potential, and finding its turning points.

**You will build:** A function that predicts the nutation range and the mean precession rate without running the time loop.

**Checkpoint (not met by the shipped code):** Mean precession for a top released from rest at 60 degrees with spin 80 rad/s within 0.3 percent of the simulation (the fast-spin formula is 3.2 percent off).

**Difficulty:** advanced

## Session 6: Spin-down and the start of the wobble

**You will learn:** Adding a spin-down torque and watching a sleeping top lose stability.

**You will build:** A simulation in which the spin decays exponentially (time constant 8 s) from 100 rad/s.

**Checkpoint (not met by the shipped code):** The tilt first exceeds 10 degrees between 6.5 s and 7.7 s, and the spin there is within 5 percent of the 47.3 rad/s sleeping limit (the shipped constant-spin code never wobbles).

**Difficulty:** advanced

## Session 7: A 3D view with the tip trace

**You will learn:** Projecting 3D attitude to a 2D animation: rotation matrices and perspective.

**You will build:** An animated top with the trace of the axis tip, the L arrow and a live precession plot.

**Checkpoint (not met by the shipped code):** A GIF of at most 48 frames and 3 MB in which the heading of the axis after one measured precession period is back within 0.05 rad of its start (modulo one full turn).

**Difficulty:** advanced

## Session 8: Torque-free tumbling: the tennis racket effect

**You will learn:** Rotation of an unsymmetric body with no torque and why one axis is unstable.

**You will build:** A body with three different moments of inertia simulated with the Euler equations.

**Checkpoint (not met by the shipped code):** Spin about the intermediate axis with a 0.1 percent perturbation flips repeatedly, with the flip period within 2 percent of the analytic value, while the energy and |L| stay constant to 1e-8.

**Difficulty:** advanced

## The final step

Combine the milestones: a quaternion-based top in 3D with a spin-down, that sleeps, wobbles and falls, with its precession and nutation checked against theory. If your result looks like the Target animation, open a pull request and tell us how you did it.
