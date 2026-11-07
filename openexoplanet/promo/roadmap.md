# Roadmap: the path to the openexoplanet Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A detrend that cannot eat the transit

**You will learn:** Masking known transits and refitting the trend (iterative detrending), and spline or Fourier-series trends.

**You will build:** A detrending routine that finds a candidate, masks its transits and refits the trend.

**Checkpoint (not met by the shipped code):** On the Session 3 demo light curve, the detrended transit keeps at least 99 percent of the true depth (the shipped 1.0 day moving median keeps 94 percent).

**Difficulty:** intermediate

## Session 5: Fit the transit with limb darkening

**You will learn:** Fitting k and the impact parameter with the limb-darkened model from Session 2 and a proper optimiser.

**You will build:** A fitting function that returns the radius ratio and impact parameter with uncertainties.

**Checkpoint (not met by the shipped code):** Radius ratio within 1 percent of the injected 0.07 on the Session 3 demo curve (the shipped grid fit gives 0.068, 2.9 percent low).

**Difficulty:** intermediate

## Session 6: A weaker planet

**You will learn:** Matched filtering, longer baselines and combining many transits to push below the noise.

**You will build:** A search that detects a 600 ppm planet (period 4.2 days) at the same noise as the demo.

**Checkpoint (not met by the shipped code):** SNR above 7 at the true period for the 600 ppm planet (the shipped search gives SNR about 4.8 at the true period on a 40-day run).

**Difficulty:** advanced

## Session 7: Unmask the binary

**You will learn:** Secondary eclipses, odd-even checks at the right period, and transit shape.

**You will build:** A vetting function that tests the folded curve at phase 0.5 and at twice the BLS period.

**Checkpoint (not met by the shipped code):** For the Session 3 eclipsing binary, report the true orbit of 6.0 days (the shipped search locks on 3.0 days).

**Difficulty:** advanced

## Session 8: Real data

**You will learn:** How public space-telescope light curves are stored, cleaned and cut into segments.

**You will build:** The full pipeline run on a downloaded real light curve of a known planet.

**Checkpoint (not met by the shipped code):** Recover the period within 0.1 percent of the published value for a known hot Jupiter (the shipped code has only been tested on synthetic data).

**Difficulty:** advanced

## The final step

Combine the milestones: a detrend that preserves the transit, a limb-darkened fit that recovers the planet size, a BLS search with a measured false-alarm threshold and a vetting step that catches binaries, run end to end on a light curve like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it.
