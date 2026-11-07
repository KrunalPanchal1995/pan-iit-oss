# Roadmap: the path to the openstressstrain Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: True stress, true strain and necking

**You will learn:** Why the engineering stress falls after the ultimate strength, and the Considere condition for the start of necking.

**You will build:** A converter from engineering to true stress and strain and a detector of the necking point on a power-law hardening metal.

**Checkpoint (not met by the shipped code):** Predicted uniform strain at necking within 5 percent of the hardening exponent n for three test metals (the shipped model never necks: its curve never falls).

**Difficulty:** intermediate

## Session 5: Fit the whole curve with uncertainty

**You will learn:** Least-squares fitting of E, the 0.2 percent yield and n, and reporting an error bar for each.

**You will build:** A fitting script with a chosen fit window and a bootstrap estimate of the spread.

**Checkpoint (not met by the shipped code):** E within 4 percent of the true value for all 50 seeds at 5 MPa noise (the shipped fixed-window fit gives up to 6.8 percent) with an uncertainty interval for E and yield.

**Difficulty:** intermediate

## Session 6: Material selection by strength per density

**You will learn:** Performance indices, and why the lightest safe tie rod is chosen by yield strength divided by density.

**You will build:** A table and an Ashby-style log-log chart of yield strength against density with a guide line.

**Checkpoint (not met by the shipped code):** The index ranks the four shipped materials with the aluminium alloy first for a strength-only 20 kN, 2 m tie, with mass about 0.90 kg (the shipped code only does the full diameter calculation).

**Difficulty:** intermediate

## Session 7: Probability of failure by Monte Carlo

**You will learn:** Treating E and yield as random numbers and estimating how often the factor of safety falls below the target.

**You will build:** A sampler that draws yield from a normal distribution and reports the failure probability.

**Checkpoint (not met by the shipped code):** Estimated probability that FoS < 2 for the 16 mm steel bar with yield normal (mean 250, sd 25 MPa) within 0.3 percentage points of the exact normal value 2.06 percent (the shipped sensitivity study gives no probability).

**Difficulty:** advanced

## Session 8: Reproduce the Target: tensile test with necking and a selection chart

**You will learn:** Combining a hardening law, necking and fracture into an animated test, with a selection chart beside it.

**You will build:** An animated specimen, a live engineering curve and a log-log chart.

**Checkpoint (not met by the shipped code):** The engineering curve peaks, then falls by at least 20 percent of the peak stress before fracture, and the area under it (energy per volume) is reported.

**Difficulty:** advanced

## The final step

Combine the milestones: a tensile test simulator that fits E, yield and hardening to noisy data, predicts necking, and recommends the lightest safe material from a selection chart with an honest uncertainty. If your result looks like the Target animation, open a pull request and tell us how you did it.
