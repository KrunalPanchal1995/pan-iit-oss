# Roadmap: the path to the openelevator Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Cleaner jerk: feed-forward the force lag

**You will learn:** Why a lagging motor force adds jerk, and how a controller can compensate for it.

**You will build:** A controller that anticipates the motor lag, so that the jerk the passengers feel stays close to the jerk of the plan.

**Checkpoint (not met by the shipped code):** On the 66.5 m express ride with a planned jerk of 1.5 m/s^3, a simulated peak jerk of at most 1.6 m/s^3 (the shipped controller gives 2.13).

**Difficulty:** intermediate

## Session 5: Fastest ride inside the comfort box

**You will learn:** Optimisation with constraints: choose acceleration, jerk and speed limits automatically.

**You will build:** A search that picks the plan with the shortest travel time whose simulated ride stays inside a peak acceleration of 1.2 m/s^2 and a peak jerk of 2.5 m/s^3.

**Checkpoint (not met by the shipped code):** A 31.5 m half-load ride of at most 15.55 s with the maximum speed kept at 2.5 m/s (the shipped plan takes 15.77 s).

**Difficulty:** intermediate

## Session 6: A day of traffic: energy over many trips

**You will learn:** Averaging over random trips and why the counterweight balance is chosen for a typical load.

**You will build:** An estimator of the energy used in a day of 200 trips with random loads and directions, compared with the counterweight mass.

**Checkpoint (not met by the shipped code):** The estimate agrees within 2 percent with a Monte Carlo run of 2000 trips while running at least 20 times faster (the shipped code only simulates one trip at a time).

**Difficulty:** intermediate

## Session 7: A stretchy rope: car vibration

**You will learn:** Why a real car bounces on its ropes and how the profile can excite or avoid it.

**You will build:** A two-mass model (car and sheave) joined by a spring that represents the rope stretch.

**Checkpoint (not met by the shipped code):** The residual car acceleration after the stop falls below 0.05 m/s^2 within 2 s with the S-curve (the shipped rigid-rope model cannot show this effect at all).

**Difficulty:** advanced

## Session 8: Two lifts, one lobby: group control

**You will learn:** How a controller decides which lift answers a call, and what waiting time means.

**You will build:** A simulation of two lifts serving a 10-floor building with random calls.

**Checkpoint (not met by the shipped code):** A mean waiting time at least 15 percent lower than the same calls served by a single lift.

**Difficulty:** advanced

## The final step

Combine the milestones: a lift controller that follows an S-curve with little added jerk, chooses its own limits inside the comfort box, and is checked against the energy balance. If your result looks like the Target animation, open a pull request and tell us how you did it.
