# Roadmap: the path to the openexperiment Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Calibrate a curved sensor

**You will learn:** Residual plots, a quadratic calibration, and why the calibrated range matters.

**You will build:** A calibration routine that fits a straight line and a quadratic, picks one by looking at the residuals, and inverts it.

**Checkpoint (not met by the shipped code):** Largest temperature error over 0 to 100 degrees C below 0.2 for the curved sensor (T + 0.002 T^2, noise sd 0.05) calibrated over the whole range (a line fitted on 0 to 50 degrees C is wrong by 10.75 degrees C at 100).

**Difficulty:** intermediate

## Session 5: Uncertainty budget for one reading

**You will learn:** Combining repeatability, calibration, quantisation and drift into one expanded uncertainty.

**You will build:** A function that returns the combined standard uncertainty of a temperature reading from its sources and the average of k readings.

**Checkpoint (not met by the shipped code):** An expanded uncertainty (coverage factor 2) of at most 0.50 degrees C for the mean of 4 readings at 50 degrees C and 5.4 V (the shipped single-reading result is about 0.58).

**Difficulty:** intermediate

## Session 6: Fewer runs: a fractional factorial

**You will learn:** Aliasing, and how to estimate three factors from half the runs.

**You will build:** A 2^(3-1) design of 4 runs per replicate that estimates three main effects of a made-up sensor.

**Checkpoint (not met by the shipped code):** The three main effects recovered within 0.3 of their true values with 8 runs in total, while the shipped 2x2 design handles only two factors per 4 runs.

**Difficulty:** advanced

## Session 7: A drift-aware recalibration schedule

**You will learn:** Random-walk drift, exceedance probability and trade-offs between cost and risk.

**You will build:** A simulation of random-walk drift that reports the longest interval keeping the chance of exceeding the tolerance below 1 percent.

**Checkpoint (not met by the shipped code):** A reported interval whose simulated exceedance is at most 1 percent (the shipped straight-line rule recalibrates every 15 days, which leaves a 2.3 percent upper-tail chance).

**Difficulty:** advanced

## Session 8: Calibrate real hardware

**You will learn:** Logging real readings from a thermistor or an Arduino-style board and checking the model against reality.

**You will build:** The same pipeline (fit, standard errors, inverse prediction, bootstrap) applied to real readings taken at three or more reference temperatures.

**Checkpoint (not met by the shipped code):** The bootstrap standard error of the slope agrees with the formula SE(m) = s / sqrt(Sxx) within 25 percent on your real data, and the residuals are shown and discussed.

**Difficulty:** advanced

## The final step

Combine the milestones: a calibration and design pipeline that fits a curved sensor, reports an uncertainty budget, chooses run orders and factor settings, and schedules recalibration, tested on real hardware. If your result looks like the Target animation, open a pull request and tell us how you did it.
