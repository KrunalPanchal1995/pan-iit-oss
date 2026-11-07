# Roadmap: the path to the opennutrition Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Estimate the hidden intake bias from weigh-ins

**You will learn:** Parameter estimation: fitting a model to noisy daily weights.

**You will build:** Simulate 8 weeks of daily weigh-ins with 0.5 kg noise for a person whose true intake is above the logged value, then estimate the bias by least squares.

**Checkpoint (not met by the shipped code):** The estimated bias is within 100 kcal/day of the truth in at least 18 of 20 random seeds (the shipped Monte Carlo leaves about 212 kcal/day, 10 percent of the intake, unresolved).

**Difficulty:** advanced

## Session 5: Fat and lean compartments

**You will learn:** Why the energy cost of a kilogram depends on what tissue is gained or lost.

**You will build:** A two-compartment model of body composition replacing the single 7700 kcal per kg constant.

**Checkpoint (not met by the shipped code):** The model reports an energy cost per kg that differs between the first and the last week of a 12 week simulation (the shipped constant 7700 never changes).

**Difficulty:** advanced

## Session 6: Rank the sources of uncertainty

**You will learn:** Sensitivity analysis: which input error matters most.

**You will build:** A variance-based sensitivity study of intake error, BMR error and portion size error.

**Checkpoint (not met by the shipped code):** A printed ranking whose first-order shares add up to between 0.9 and 1.0 of the output variance (the shipped code reports only the combined spread of about 5.8 kg).

**Difficulty:** intermediate

## Session 7: Weekly schedules with weekends

**You will learn:** Time-varying inputs and averaging.

**You will build:** A model whose intake and walking differ between weekdays and weekends.

**Checkpoint (not met by the shipped code):** After 12 weeks the 7-day-average mass matches the constant-average-input solution within 0.05 kg (the shipped model accepts only constant inputs).

**Difficulty:** intermediate

## Session 8: Reproduce the Target animation

**You will learn:** Animating a model with bars, a trajectory and an uncertainty band.

**You will build:** An animated GIF with the energy-in and energy-out bars, the mass curve, the naive line and a shaded band.

**Checkpoint (not met by the shipped code):** A GIF of at most 3 MB and at most 60 frames in which the band widens with time and the curve visibly flattens toward the steady state.

**Difficulty:** advanced

## The final step

Combine the milestones: a model fitted to noisy weigh-ins, with uncertainty bands and a clear statement of what it cannot tell. If your result looks like the Target animation, open a pull request and tell us how you did it. Always remember this repo is general education, not medical or dietary advice.
