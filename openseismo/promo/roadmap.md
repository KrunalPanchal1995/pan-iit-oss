# Roadmap: the path to the openseismo Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Survive a bad pick

**You will learn:** Outliers, robust fitting and residual checks.

**You will build:** A location routine that spots and drops (or down-weights) a blunder in one pick.

**Checkpoint (not met by the shipped code):** A +3 s blunder in any one of the five picks moves the epicentre by less than 1 km (the shipped code is off by between 5 and 9 km).

**Difficulty:** intermediate

## Session 5: Fix the network

**You will learn:** Reading condition numbers and dilution to design a network.

**You will build:** A tool that suggests where to put one more station.

**Checkpoint (not met by the shipped code):** For the one-sided network, one added station brings the horizontal dilution below 12 km/s (the shipped network has 85 km/s).

**Difficulty:** intermediate

## Session 6: Use the layers

**You will learn:** Putting a layered velocity model inside the forward calculation.

**You will build:** A locator that predicts first arrivals with the two-layer model instead of one speed.

**Checkpoint (not met by the shipped code):** The epicentre error for the two-layer toy falls below 0.1 km for both networks (the shipped constant-speed code gives 1.32 km and 19.0 km).

**Difficulty:** advanced

## Session 7: Add depth

**You will learn:** A fourth unknown, trade-offs between depth and origin time, and 3-D geometry.

**You will build:** A four-unknown locator (x, y, depth, t0) with a vertical error bar.

**Checkpoint (not met by the shipped code):** On a synthetic quake at 10 km depth, recover the depth within 2 km with eight stations and 0.1 s picks (the shipped code has no depth at all).

**Difficulty:** advanced

## Session 8: Reproduce the Target animation

**You will learn:** Animating wavefronts, seismograms and the shrinking ellipse together.

**You will build:** A GIF of expanding P and S wavefronts, per-station seismograms with picks and the iteration path.

**Checkpoint (not met by the shipped code):** A GIF of at most 60 frames and 3 MB in which the ellipse area decreases at every iteration shown.

**Difficulty:** advanced

## The final step

Combine the milestones: a locator that rejects bad picks, uses a layered speed model and a fourth unknown for depth, and an animation that shows the waves, the picks and the shrinking ellipse. If your result looks like the Target animation, open a pull request and tell us how you did it. Remember that all of this works after the quake, with recorded data; it is not a prediction or warning tool.
