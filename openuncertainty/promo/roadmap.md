# Roadmap: the path to the openuncertainty Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Correlated inputs for any number of variables

**You will learn:** How a correlation matrix and its Cholesky factor create correlated random inputs.

**You will build:** A sampler that draws three inputs with a given correlation matrix and propagates them.

**Checkpoint (not met by the shipped code):** The sample correlation matrix of 100000 draws is within 0.01 of the target for three inputs (the shipped code links only two inputs).

**Difficulty:** intermediate

## Session 5: Which input matters? Sobol indices

**You will learn:** Variance-based sensitivity indices for models that are not straight lines.

**You will build:** A sampling estimator of first-order indices for the Ishigami test function.

**Checkpoint (not met by the shipped code):** First-order indices of about 0.31, 0.44 and 0.00 within 0.03 using 20000 samples per estimate (the variance shares of Session 2 cannot see interactions).

**Difficulty:** advanced

## Session 6: Beyond first order: the mean shifts

**You will learn:** The second-order term, which moves the mean as well as the spread.

**You will build:** A second-order propagation function for the ratio x / y.

**Checkpoint (not met by the shipped code):** Predict the mean shift of x / y for a 10 percent denominator error to within 10 percent of the Monte Carlo value of 0.02 (the shipped linear formula predicts 0).

**Difficulty:** intermediate

## Session 7: A cheap stand-in for a slow model

**You will learn:** Replacing an expensive formula by a fitted polynomial and propagating through that.

**You will build:** A quadratic surrogate of the pendulum g built from 9 model runs.

**Checkpoint (not met by the shipped code):** The surrogate gives a spread of g within 2 percent of the direct Monte Carlo value of 0.109 m/s^2 using only 9 evaluations of the true model.

**Difficulty:** advanced

## Session 8: Animate the propagation

**You will learn:** How to show convergence of a histogram as the number of draws grows.

**You will build:** A looping GIF of an input cloud, an output histogram and an error budget, like the Target.

**Checkpoint (not met by the shipped code):** At most 60 frames and under 3 MB, with the spread in the final frame within 1 percent of the 100000-draw value.

**Difficulty:** advanced

## The final step

Combine the milestones: a tool that takes a formula, input values, uncertainties and correlations, and returns the budget, the linear and Monte Carlo intervals and an animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
