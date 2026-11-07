# Roadmap: the path to the openfractal Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Zoom beyond float64 with perturbation

**You will learn:** Reference orbits in high precision, and why small differences from them can be computed in ordinary floats.

**You will build:** A deep-zoom renderer that keeps one high-precision orbit and perturbs around it.

**Checkpoint (not met by the shipped code):** A frame at window width 1e-30 with all 200 columns resolved and visible structure (the shipped renderer resolves only 1 distinct column at 1e-16).

**Difficulty:** advanced

## Session 5: Skip the interior

**You will learn:** Closed-form tests for the main cardioid and the period-2 bulb, and detecting periodic orbits early.

**You will build:** A faster renderer that returns the same picture for the same window.

**Checkpoint (not met by the shipped code):** The 160 by 100 full-set picture at max_iter = 2000 with identical inside/outside labels in at most 1.5 million z-updates (the shipped renderer needs 6.8 million).

**Difficulty:** intermediate

## Session 6: A better area estimate

**You will learn:** Variance reduction: stratified sampling, or sampling only boundary cells.

**You will build:** A second area estimator with a proper error bar.

**Checkpoint (not met by the shipped code):** With N = 100,000 points an estimate within 0.01 of 1.5066 and a reported error bar of at most 0.002 (the shipped Monte Carlo gives a bar of 0.008).

**Difficulty:** intermediate

## Session 7: A looping Julia morph

**You will learn:** Parameter paths: moving c along a closed curve and keeping colours steady between frames.

**You will build:** A Julia-set animation as GIF or MP4 with c on a closed path.

**Checkpoint (not met by the shipped code):** A loop of 48 frames whose last frame differs from the first by less than 1e-6 (the shipped repo has no animation).

**Difficulty:** intermediate

## Session 8: Zoom video with automatic iterations

**You will learn:** Choosing max_iter per frame from the zoom, and exponential zoom speed.

**You will build:** A 120-frame zoom video that keeps the share of wrongly-inside pixels below 1 percent in every frame.

**Checkpoint (not met by the shipped code):** A video of at least 120 frames with the error of Session 2's measure at most 1 percent in each frame, ending at a window width of at most 1e-10.

**Difficulty:** advanced

## The final step

Combine the milestones: a zoom video far below 1e-13 beside a looping Julia morph, with a fast renderer and honest error bars. If your result looks like the Target animation, open a pull request and tell us how you did it.
