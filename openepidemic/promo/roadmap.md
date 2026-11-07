# Roadmap: the path to the openepidemic Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Add age groups

**You will learn:** Why a contact matrix between groups changes who should be protected first, and how to build a two-group SIR.

**You will build:** A two-group SIR model (for example children and adults) with a 2 by 2 contact matrix and group-specific vaccination.

**Checkpoint (not met by the shipped code):** With identical groups and equal contacts it reproduces the single-group peak of 1538.8 people to within 0.1 percent, and total people are conserved to 1e-6 (the shipped single-group code cannot do either).

**Difficulty:** intermediate

## Session 5: Add an exposed stage (SEIR)

**You will learn:** Latent periods, and how they slow the early growth without changing the final size.

**You will build:** An SEIR model with latent rate sigma, solved with your RK4.

**Checkpoint (not met by the shipped code):** With sigma = 0.5 per day the measured early growth rate matches the positive root of (r + sigma)(r + gamma) = beta sigma within 1 percent, and the final size still matches z = 1 - exp(-R0 z).

**Difficulty:** intermediate

## Session 6: Fit with a reporting delay and under-reporting

**You will learn:** How to add nuisance parameters to a fit and what they cost in identifiability.

**You will build:** A fit of beta, gamma, delay and reporting fraction to synthetic data that has a 5-day delay.

**Checkpoint (not met by the shipped code):** Recover beta within 5 percent of 0.4 from data with a 5-day delay (the shipped fit gives 0.308, 23 percent low).

**Difficulty:** advanced

## Session 7: Honest uncertainty with a Bayesian fit

**You will learn:** Likelihoods, priors and credible intervals instead of repeated grid fits.

**You will build:** A random-walk Metropolis sampler for beta and gamma with a Poisson likelihood.

**Checkpoint (not met by the shipped code):** The 90 percent credible interval for beta from 14 days of data covers the truth in at least 85 of 100 repeated data sets and is wider than 0.15 (the shipped code only reports a standard deviation of 0.08).

**Difficulty:** advanced

## Session 8: Target: the animated fit band and vaccination slider

**You will learn:** Putting the whole pipeline in one animation: sweep vaccination and refit as days arrive.

**You will build:** A two-panel animation like the Target, built on your own fitting and RK4 code.

**Checkpoint (not met by the shipped code):** The animation shows the 10 to 90 percent band of the daily-case curve narrowing as days of data are added: its widest point is below 5 percent of the true peak once 40 days of data are used (it is about half the true peak with 14 days). The shipped code makes no band at all.

**Difficulty:** advanced

## The final step

Combine the milestones: an age-structured SEIR model fitted with a reporting delay, an honest credible band, and a vaccination study under a capacity line, shown in an animation like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it. Keep it synthetic, keep it a teaching tool.
