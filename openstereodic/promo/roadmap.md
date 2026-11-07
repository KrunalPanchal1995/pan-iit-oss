# Roadmap: the path to the openstereodic Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Second-order shape function

**You will learn:** Why an affine subset is biased by curved displacement and how a quadratic shape function removes it.

**You will build:** A matching function with a quadratic shape function (12 parameters) and a test on a strongly curved field.

**Checkpoint (not met by the shipped code):** RMS displacement error of 0.02 px or less at subset half-size 25 for curvature b = 4e-4 per pixel, noise-free (the shipped affine subset gives 0.086 px).

**Difficulty:** intermediate

## Session 5: Large motion and seed propagation

**You will learn:** Reliability-guided tracking: start at one good point and pass the answer to neighbours, plus coarse-to-fine search.

**You will build:** A tracker that follows a whole grid through displacements far larger than the search window.

**Checkpoint (not met by the shipped code):** A 15 px rigid shift recovered to 0.02 px at every grid point (the shipped search window of 6 px returns 6 px, i.e. 9 px wrong).

**Difficulty:** intermediate

## Session 6: Calibrate the stereo rig

**You will learn:** Estimating focal length, baseline and principal point from images of a known dot grid.

**You will build:** A calibration routine and a reprojection-error report.

**Checkpoint (not met by the shipped code):** Baseline recovered to within 0.5 percent from 20 images with 0.1 px noise (the shipped code assumes the values are exactly known, so a 2 percent error in B gives 10 mm of depth error at 0.5 m).

**Difficulty:** advanced

## Session 7: 3D strain on a curved surface

**You will learn:** Green-Lagrange strain from a 3D displacement field and why one camera is fooled by out-of-plane motion.

**You will build:** A stereo pipeline that reconstructs a bulging specimen and reports the strain along it.

**Checkpoint (not met by the shipped code):** RMS error of the strain in x below 0.005 up to 12 percent strain with 18 mm of out-of-plane motion, where a single camera is wrong by more than 0.02 at the waist.

**Difficulty:** advanced

## Session 8: A load history

**You will learn:** Tracking over many load steps, initialising from the previous step and avoiding drift.

**You will build:** An animation of the measured strain map over 30 load steps.

**Checkpoint (not met by the shipped code):** RMS strain error below 0.003 at every one of 30 load steps, and a correlation above 0.99 at every tracked point.

**Difficulty:** advanced

## The final step

Combine the milestones: a calibrated stereo rig, a robust tracker with a higher-order shape function, and a 3D strain map of a loaded, bulging strip. If your result looks like the Target animation, open a pull request and tell us how you did it.
