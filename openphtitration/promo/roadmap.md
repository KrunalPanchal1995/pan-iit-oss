# Roadmap: the path to the openphtitration Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Fit the whole curve

**You will learn:** Least-squares fitting of a model curve to noisy titration data instead of reading only the peak.

**You will build:** A fitting routine that adjusts the concentration (and pKa) to minimise the squared pH residuals.

**Checkpoint (not met by the shipped code):** Scatter of the fitted equivalence volume of at most 0.04 mL over 200 noisy runs with volume noise 0.03 mL, pH noise 0.02 and 0.2 mL steps (the shipped derivative peak gives about 0.055 mL).

**Difficulty:** intermediate

## Session 5: Identify an unknown acid by its pKa

**You will learn:** Reading pKa from the half-equivalence point of noisy data and matching it to a table.

**You will build:** A function that estimates pKa and the concentration from one run and names the closest acid in a small table.

**Checkpoint (not met by the shipped code):** pKa estimate within 0.05 of the true value in at least 95 percent of 200 noisy runs (the shipped code reports no pKa at all).

**Difficulty:** intermediate

## Session 6: A diprotic acid with two jumps

**You will learn:** Two dissociation constants, two buffer regions and two equivalence points.

**You will build:** A charge-balance solver for a diprotic acid titrated with a strong base.

**Checkpoint (not met by the shipped code):** For a test acid with pKa1 = 2.0 and pKa2 = 7.0: second equivalence volume equal to twice the first within 0.5 percent, and pH at 1.5 times the first volume within 0.05 of pKa2 (the shipped monoprotic code has one jump only).

**Difficulty:** advanced

## Session 7: When 25 C is not enough

**You will learn:** How temperature changes Kw and why neutral is not always pH 7.

**You will build:** A solver whose Kw is a parameter, with a neutral-pH function.

**Checkpoint (not met by the shipped code):** Neutral pH for Kw = 5.5e-14 (an approximate value near 50 C) equals 6.63 within 0.01, while the shipped model with a fixed Kw = 1e-14 gives 7.00.

**Difficulty:** advanced

## Session 8: Animate the titration

**You will learn:** Drawing a burette, a flask whose colour follows the pH and a live curve with a derivative panel.

**You will build:** A GIF of at most 60 frames and 3 MB in which the burette empties, the flask colour changes and the derivative peak is marked.

**Checkpoint (not met by the shipped code):** The final frame states the equivalence volume within 0.1 mL of the true value and the concentration within 1 percent.

**Difficulty:** advanced

## The final step

Combine the milestones: a titration analyser that reads noisy data, fits the curve, reports the pKa and concentration with an uncertainty, and exports an animation like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it.
