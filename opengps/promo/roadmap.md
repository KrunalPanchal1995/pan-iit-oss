# Roadmap: the path to the opengps Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Real orbits instead of fixed toy positions

**You will learn:** Circular and then elliptical orbits, Kepler's third law and how a satellite position depends on time.

**You will build:** An orbit propagator that gives each satellite position at any time, replacing the fixed toy positions.

**Checkpoint (not met by the shipped code):** A satellite at 26,560 km returns to its starting position within 1 m after one orbital period (about 11.97 hours; the shipped code has no motion at all).

**Difficulty:** intermediate

## Session 5: Atmosphere delay

**You will learn:** Why signals slow down in the atmosphere, more for low satellites, and how a simple elevation-dependent model removes most of it.

**You will build:** A delay model added to the simulated ranges and a correction in the solver.

**Checkpoint (not met by the shipped code):** With a 2.5 m / sin(elevation) delay on every range, the fix error falls below 2 m (the shipped solver gives 8.9 m for the same data, without noise).

**Difficulty:** intermediate

## Session 6: Weight the satellites

**You will learn:** Weighted least squares, and why low satellites with noisier ranges should count less.

**You will build:** A weighted Gauss-Newton solver with elevation-dependent noise.

**Checkpoint (not met by the shipped code):** With noise sigma = 3 + 12 exp(-elevation / 12 degrees) m on eight satellites, the rms error over 1000 trials falls below 7.8 m (the shipped unweighted solver gives 8.26 m).

**Difficulty:** advanced

## Session 7: Detect and exclude a faulty satellite

**You will learn:** Residual tests and consistency checks, and why a fault is hidden when only four satellites are used.

**You will build:** A fault detector that flags and removes one bad range.

**Checkpoint (not met by the shipped code):** With a 200 m error on one of eight satellites plus 5 m noise, the final fix error is below 25 m (the shipped solver gives 194 m even without noise).

**Difficulty:** advanced

## Session 8: Velocity from Doppler

**You will learn:** How the change in signal frequency gives the receiver's speed, and how to solve for velocity and clock drift together.

**You will build:** A second linear solve for the velocity and clock drift of a moving receiver.

**Checkpoint (not met by the shipped code):** The speed of a simulated walking receiver is recovered to within 0.1 m/s (the shipped code estimates no velocity).

**Difficulty:** advanced

## The final step

Combine the milestones: real orbits, an atmosphere model, a weighted and fault-tolerant solver and a relativity-corrected satellite clock, giving a fix of a moving receiver with an error budget. If your result looks like the Target animation, open a pull request and tell us how you did it.
