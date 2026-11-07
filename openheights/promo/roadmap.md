# Roadmap: the path to the openheights Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Calibrate the phone

**You will learn:** How a constant offset in the tilt sensor creates a bias that averaging cannot remove, and how flipping the phone cancels it.

**You will build:** A small model of a clinometer with an offset and noise, and a calibration routine that uses readings from both sides.

**Checkpoint (not met by the shipped code):** A phone with a 0.8 degree offset gives a height bias of 0.79 m at 45 degrees and 28.4 m (the shipped code just averages it); your calibrated estimate must have a bias of at most 0.1 m.

**Difficulty:** intermediate

## Session 5: Outlier-proof averaging

**You will learn:** Why a few wild readings (a bump, a sneeze) ruin a mean and how the median and robust spreads help.

**You will build:** An estimator that rejects outliers and still reports an uncertainty.

**Checkpoint (not met by the shipped code):** With 5 percent of 100 readings off by 5 to 10 degrees, the root-mean-square error of the shipped mean is about 0.19 m; yours must stay at 0.10 m or below.

**Difficulty:** intermediate

## Session 6: Measure a leaning tree

**You will learn:** Why the one-angle formula fails when the top is not above the base, and how three stations fix it.

**You will build:** A solver that finds the vertical height and the lean angle from readings taken from several places.

**Checkpoint (not met by the shipped code):** A 20 m tree leaning 10 degrees towards you at 30 m: the shipped formula returns 22.07 m for a true vertical height of 19.70 m; yours must recover the vertical height to within 0.5 m.

**Difficulty:** advanced

## Session 7: Unknown ground: three stations

**You will learn:** Solving for the tower position and height together when the distance to the base cannot be measured and the ground is not level.

**You will build:** A least-squares fit of height and base position from readings at three non-collinear stations.

**Checkpoint (not met by the shipped code):** Recover the height of a 30 m tower and its base position to within 0.5 m with noisy readings (sigma = 0.5 degrees) using a total of 30 readings.

**Difficulty:** advanced

## Session 8: Animate the walk-away estimate

**You will learn:** Streaming an estimate and its error band as each reading arrives, with weights for the quality of each stop.

**You will build:** A looping animation of an observer walking away from a tower with sight lines and a converging estimate.

**Checkpoint (not met by the shipped code):** A GIF of at most 60 frames whose last frame shows a 2-sigma band of at most 0.2 m around the true height.

**Difficulty:** advanced

## The final step

Combine the milestones: a phone-based measuring routine that calibrates the sensor, rejects outliers, works on a slope and reports a height with an honest uncertainty. Then measure a real tree and a real tower and compare. If your result looks like the Target animation, open a pull request and tell us how you did it.
