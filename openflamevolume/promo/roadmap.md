# Roadmap: the path to the openflamevolume Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Camera calibration from a checkerboard

**You will learn:** That Session 1 assumed known f and positions; real cameras must be calibrated, and what the reprojection error tells you.

**You will build:** A function that finds the focal length and camera pose from the corners of a flat checkerboard seen in a few photos, using a direct linear transform and a least-squares fit.

**Checkpoint (not met by the shipped code):** On synthetic corners with 0.2 px noise the mean reprojection error is below 0.3 px and the recovered focal length is within 1 percent of the true one (the shipped code assumes perfect calibration).

**Difficulty:** intermediate

## Session 5: Cameras that are not parallel: epipolar geometry

**You will learn:** How a point in one image constrains a line in the other, and why toed-in cameras see the flame better.

**You will build:** General triangulation from two projection matrices (cameras that toe in towards the flame) and a search along the epipolar line instead of along the image row.

**Checkpoint (not met by the shipped code):** For two cameras toed in by 10 degrees each, the triangulated points of the Session 3 flame are within 0.1 mm of the truth when the matches are exact (the shipped code only handles parallel pairs).

**Difficulty:** intermediate

## Session 6: A flickering flame: volume against time

**You will learn:** Time series of an experiment, sampling and the Nyquist limit, and what camera synchronisation does to the error.

**You will build:** Render a flame whose height oscillates at 10 Hz, reconstruct the volume frame by frame and find the flicker frequency with a Fourier transform.

**Checkpoint (not met by the shipped code):** The recovered flicker frequency is within 0.5 Hz of 10 Hz from 60 frames at 120 frames per second (the shipped code has a single steady flame).

**Difficulty:** intermediate

## Session 7: The error budget of the whole pipeline

**You will learn:** How errors combine, which error dominates and how to report a result as value plus uncertainty.

**You will build:** A Monte Carlo study that adds matching noise, a calibration error and a camera position error and reports the volume uncertainty as a spread.

**Checkpoint (not met by the shipped code):** The Monte Carlo volume spread agrees with a first-order error-propagation estimate to within 20 percent for small errors (the shipped code only studies matching noise on the area).

**Difficulty:** advanced

## Session 8: Rebuild the inside of a translucent flame

**You will learn:** That a real flame is a volume of light, not a surface, and what emission tomography does about it.

**You will build:** An algebraic reconstruction (ART) of the glow of a translucent, axisymmetric flame from line-of-sight sums seen by at least three directions.

**Checkpoint (not met by the shipped code):** A known Gaussian emission profile is recovered with an RMS error below 5 percent of its peak from 4 views with 2 percent noise (the shipped code treats the flame as an opaque surface).

**Difficulty:** advanced

## The final step

Combine the milestones: calibrated, toed-in cameras around a flickering flame, a volume against time with an uncertainty from the whole error budget, and a rebuilt interior of the glow. If your result looks like the Target and reports its own error bar, open a pull request and tell us how you did it.
