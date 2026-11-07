# Roadmap: the path to the openheatspread Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: An implicit solver with no step limit

**You will learn:** Backward Euler and Crank-Nicolson: solving a linear system each step so that the time step is not tied to dx.

**You will build:** A second solver that runs the Gaussian test with steps many times larger than the explicit limit.

**Checkpoint (not met by the shipped code):** On the dx = 0.5 mm Gaussian test with alpha = 20 mm^2/s, run at r = 5 (20 times the explicit limit) and keep the largest error below 0.05 K after 1 s (the shipped explicit solver blows up at r = 5).

**Difficulty:** intermediate

## Session 5: A heat pipe between the chips and the edge

**You will learn:** A strip of very high conductivity as a fast heat road, and how it changes the hot spots.

**You will build:** A board model with a high-conductance strip connecting the CPU to the board edge.

**Checkpoint (not met by the shipped code):** For the 12 W CPU plus 8 W GPU on a 0.5 mm sheet with h = 40, bring the peak rise below 55 K (the shipped model gives 76.3 K).

**Difficulty:** intermediate

## Session 6: Go 3D: a stack of chip, board and spreader

**You will learn:** A 3D explicit solver and its stability limit dt <= dx^2 / (6 alpha), and how to check it against a 3D exact Gaussian.

**You will build:** The same validation in three dimensions with layers of different materials.

**Checkpoint (not met by the shipped code):** The 3D Gaussian test (alpha = 20 mm^2/s, s0 = 3 mm, 60 K start) reproduces the exact peak rise of 4.72 K at 1 s within 1 percent.

**Difficulty:** advanced

## Session 7: Reproduce the Target: bare board against spreader

**You will learn:** Time-varying chip power (burst, load, idle) and a side-by-side comparison with and without a spreader.

**You will build:** A transient simulation of two chips switching on and off and an animated heat map.

**Checkpoint (not met by the shipped code):** For chips of 6.5 W and 4.3 W on a 100 mm x 60 mm board, the bare board's peak rise is at least 3 times that with a 0.25 mm copper spreader (the Target shows about 86 K against 27 K).

**Difficulty:** advanced

## Session 8: Find the hot spots from a few sensors

**You will learn:** An inverse problem: estimating the unknown chip powers from temperatures measured at a few points.

**You will build:** A script that recovers CPU and GPU power from three noisy sensor readings.

**Checkpoint (not met by the shipped code):** Recover both chip powers within 5 percent from three simulated sensor readings that carry 0.5 K of noise.

**Difficulty:** advanced

## The final step

Combine the milestones: a laptop board model with a heat pipe and a spreader, driven by a changing chip load, whose animated heat map and thermal budget look like the Target. If your result matches the Target animation, open a pull request and tell us how you did it.
