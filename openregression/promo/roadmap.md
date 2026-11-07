# Roadmap: the path to the openregression Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Intervals when the noise grows

**You will learn:** Heteroscedastic noise: why the 95 percent interval of Session 2 under-covers when the spread depends on rain, and how weighted least squares or a variance model repairs it.

**You will build:** A prediction interval that estimates the noise level as a function of rain.

**Checkpoint (not met by the shipped code):** Coverage of at least 0.93 at 850 mm over 2000 repeats when the noise sd is 0.1 x rain (100 mm) - 0.1 t/ha (the shipped interval covers about 0.84).

**Difficulty:** intermediate

## Session 5: A smooth model without choosing a degree

**You will learn:** Kernel ridge or splines: flexible curves controlled by one smoothness setting chosen by cross-validation.

**You will build:** A smoother that replaces the polynomial in the degree-versus-error experiment.

**Checkpoint (not met by the shipped code):** Test RMSE of at most 0.34 t/ha on the 500 fresh seasons of the Session 3 experiment, with settings chosen by cross-validation only (the shipped best polynomial gives 0.365 and the shipped ridge 0.371).

**Difficulty:** intermediate

## Session 6: Models that switch features off

**You will learn:** The L1 penalty (lasso) and why it sets coefficients exactly to zero while ridge only shrinks them.

**You will build:** A lasso solver by coordinate descent, written from the roadmap.

**Checkpoint (not met by the shipped code):** With 10 candidate inputs of which 3 matter, exactly 7 coefficients come out exactly zero and the 3 true ones are non-zero (the shipped ridge leaves 0 coefficients exactly zero).

**Difficulty:** advanced

## Session 7: Planning for a bad season

**You will learn:** Quantile regression: fit the yield that 10 percent of seasons fall below instead of the average.

**You will build:** A line fitted by minimising the pinball loss.

**Checkpoint (not met by the shipped code):** On 20000 fresh seasons the fitted line has a fraction between 0.09 and 0.11 of seasons below it (the shipped least-squares line has about 0.51 below it).

**Difficulty:** advanced

## The final step

Combine the milestones: a yield model with a smooth response, honest intervals when the noise grows, and a quantile line for bad seasons, shown in a four-panel animation like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it.
