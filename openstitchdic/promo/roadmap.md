# Roadmap: the path to the openstitchdic Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Lens distortion

**You will learn:** Radial lens distortion and how to estimate and remove it before the homography.

**You will build:** A distortion model (one radial term) fitted from the sheet corners and edge points, applied before warping.

**Checkpoint (not met by the shipped code):** For a camera with 3 percent barrel distortion at the picture corner, the nine subset centres land within 0.1 px of their true grid positions (the shipped homography has no distortion term and cannot meet this).

**Difficulty:** intermediate

## Session 5: Calibration targets and 3-D triangulation

**You will learn:** Calibrating both cameras from a known dot grid and triangulating depth, so out-of-plane motion is seen.

**You will build:** A calibration routine plus triangulation of matched points into millimetres.

**Checkpoint (not met by the shipped code):** Reprojection error below 0.3 px on a synthetic dot grid and an out-of-plane step of 1 mm recovered to within 0.05 mm (the shipped code is planar and has no calibration).

**Difficulty:** advanced

## Session 6: Rolling-shutter correction

**You will learn:** Why each image row of a rolling-shutter camera has its own time, and how to timestamp rows.

**You will build:** A simulator with a row-by-row readout and a correction that resamples each row in time.

**Checkpoint (not met by the shipped code):** With a 10 ms top-to-bottom readout, the merged RMS error on the step-like motion stays below 0.05 px (the shipped pipeline treats each picture as one instant).

**Difficulty:** advanced

## Session 7: Correlation at GPU speed

**You will learn:** Computing correlation for thousands of subsets at once with FFTs or vectorised code on a GPU.

**You will build:** A batched correlator that handles a 100 x 100 grid of subsets per frame pair.

**Checkpoint (not met by the shipped code):** 10,000 subsets per frame pair in under 1 s, with results equal to the shipped one-subset-at-a-time loop to within 0.01 px (the shipped loop takes several seconds).

**Difficulty:** advanced

## Session 8: Your own cameras

**You will learn:** Real pictures: how to pick landmarks, estimate the clock offset and report an honest error.

**You will build:** A run of Session 3 on your own two videos, with points.txt, an estimated offset and a written error budget.

**Checkpoint (not met by the shipped code):** Warped picture B correlates with picture A above 0.95, and a known stage move of your sample is measured to within 0.1 px.

**Difficulty:** intermediate

## The final step

Combine the milestones: undistort, calibrate, align in time with row timestamps, correlate quickly, and merge two real cameras into one clean data set with an honest error estimate. If your result looks like the Target animation, open a pull request and tell us how you did it.
