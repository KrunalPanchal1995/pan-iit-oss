# Roadmap: the path to the openodds Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Importance sampling for a rare event

**You will learn:** Why plain simulation fails for tiny probabilities and how sampling the rare event on purpose and re-weighting fixes it.

**You will build:** An estimator of the probability that 8 dice all show 6 (exactly 6^-8) that samples biased dice and weights each sample.

**Checkpoint (not met by the shipped code):** Estimate 6^-8 = 5.95e-7 to within 10 percent relative error using at most 100000 samples (plain simulation would need about 168 million).

**Difficulty:** advanced

## Session 5: The full poker table

**You will learn:** Counting the nine hand types by combinations without double counting.

**You will build:** A function returning the count of every hand type for 5-card poker, checked against simulation.

**Checkpoint (not met by the shipped code):** The nine type counts add up to 2,598,960 exactly (the shipped code counts only two types).

**Difficulty:** intermediate

## Session 6: Lottery prize tiers and honest expected value

**You will learn:** Hypergeometric counting: matching 3, 4, 5 or 6 numbers.

**You will build:** A table of the number of draws for each match count and the expected return for an illustrative prize list.

**Checkpoint (not met by the shipped code):** Draws with exactly 6, 5, 4 and 3 matches are 1, 258, 13545 and 246820, and all match counts add up to 13,983,816.

**Difficulty:** intermediate

## Session 7: Conditional probability: Monty Hall

**You will learn:** Conditional probability and Bayes' rule, and why intuition fails.

**You will build:** A seeded simulation of the game with a confidence statement from the standard error.

**Checkpoint (not met by the shipped code):** Switching wins 2/3 and staying wins 1/3, each within 0.005 using the number of trials your own error formula asks for.

**Difficulty:** intermediate

## Session 8: Animate convergence like the Target

**You will learn:** Reusing one stream of random trials to draw an experiment growing frame by frame, with error bands.

**You will build:** An animation of simulated dice-sum frequencies and a birthday curve converging with 95 percent bands.

**Checkpoint (not met by the shipped code):** A GIF of at least 40 frames in which the worst dice-sum error at the last frame is below 0.005 and the birthday estimate at 23 people is within 0.01 of 0.507.

**Difficulty:** advanced

## The final step

Combine the milestones: an experiment that estimates several probabilities with honest error bands, handles a rare event with importance sampling, and exports a clean animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
