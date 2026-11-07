# Roadmap: the path to the opensymbolic Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Constants inside the formula

**You will learn:** Nonlinear least squares (for example Levenberg-Marquardt) so that a formula such as a x / (1 + b x) can have its constants fitted.

**You will build:** A search that fits two constants inside the formula by iteration, not only a and b outside.

**Checkpoint (not met by the shipped code):** Recover y = 5 x / (1 + 0.37 x) at 5 percent noise in at least 90 percent of 40 seeded trials (the shipped search recovers it in 0 percent).

**Difficulty:** intermediate

## Session 5: More than one input

**You will learn:** Expression trees with several variables, and how the search space grows.

**You will build:** A search over formulas in x1 and x2 that recovers r = x1 sqrt(x2).

**Checkpoint (not met by the shipped code):** At least 90 percent recovery at 5 percent noise (the shipped search accepts a single input only).

**Difficulty:** intermediate

## Session 6: Weighted errors

**You will learn:** Giving each data point a weight inverse to its uncertainty, as in literature rate data.

**You will build:** A weighted least-squares version of the search.

**Checkpoint (not met by the shipped code):** On y = 3 x^2 with half the points at 2 percent noise and half at 50 percent, recover the law in at least 95 percent of 40 seeded trials (the shipped unweighted search recovers it in 80 percent).

**Difficulty:** advanced

## Session 7: A genetic search for bigger spaces

**You will learn:** Random trees, crossover, mutation and selection, so that you need not list every formula (the shipped enumeration holds 296966 distinct formulas at 9 nodes and grows about five times per extra node).

**You will build:** A genetic loop with a complexity penalty.

**Checkpoint (not met by the shipped code):** Recover the 10-node law y = sqrt(x) / (1 + x^2) + ln(x) in at least 80 percent of 20 seeded trials at 2 percent noise, with each run under 30 seconds (the shipped search stops at 7 nodes).

**Difficulty:** advanced

## Session 8: Leave-one-class-out validation

**You will learn:** Testing a discovered rule on a whole held-out family of cases, as research on rate rules does.

**You will build:** A validation function that holds out one class of synthetic reactions at a time.

**Checkpoint (not met by the shipped code):** A discovered rule whose held-out-class error is within a factor of 2 of its training error on four synthetic reaction classes.

**Difficulty:** advanced

## The final step

Combine the milestones: a genetic search for formulas in several variables with weighted errors and held-out validation, which rediscovers a law you chose, from noisy data and in a few seconds. If your result looks like the Target animation, open a pull request and tell us how you did it.
