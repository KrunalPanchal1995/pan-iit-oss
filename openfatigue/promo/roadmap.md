# Roadmap: the path to the openfatigue Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Fatigue notch factor K_f

**You will learn:** Why a sharp notch hurts less than K_t suggests, through notch sensitivity and notch radius.

**You will build:** A function that returns K_f between 1 and K_t from the notch radius and the material, used in the plate-with-hole life.

**Checkpoint (not met by the shipped code):** For a hole in a wide plate with a nominal amplitude of 110 MPa and zero mean, the predicted life is at least three times the 326,000 cycles that the shipped K_t = 3 model gives.

**Difficulty:** intermediate

## Session 5: Beyond the straight line: low cycles and the knee

**You will learn:** Why the Basquin line cannot hold at very high stress, and how a strain-based curve joins the two regimes.

**You will build:** A strain-life curve with an elastic and a plastic part, joined to the S-N line.

**Checkpoint (not met by the shipped code):** The predicted life stays finite and falls monotonically all the way to an amplitude above the 600 MPa ultimate strength (the shipped line only extrapolates).

**Difficulty:** advanced

## Session 6: Reliability design life

**You will learn:** How scatter turns a median life into a life that 99 percent of parts reach.

**You will build:** A function that gives the design life for a chosen reliability from the median life and the log scatter.

**Checkpoint (not met by the shipped code):** For a median life of 100,000 cycles and a scatter of 0.3 it returns a 99 percent life within 5 percent of 20,000 cycles (the shipped Monte Carlo shows the 1st percentile is about 0.19 of the median).

**Difficulty:** intermediate

## Session 7: Overload retardation in crack growth

**You will learn:** How one large overload delays later crack growth, which the order-blind models cannot show.

**You will build:** A crack growth integrator that tracks the overload plastic zone and slows growth behind it.

**Checkpoint (not met by the shipped code):** After a single overload of twice the normal stress, the predicted remaining life is at least 10 percent longer than with the shipped order-independent Paris model.

**Difficulty:** advanced

## Session 8: Reproduce the Target: initiation plus propagation

**You will learn:** How to chain the S-N and Miner stage to the Paris stage on one clock and animate it.

**You will build:** An animation with an S-N operating point, a plate with a growing crack and two bars.

**Checkpoint (not met by the shipped code):** The damage bar reaches exactly 1.0 on the frame where the crack appears, and the crack bar reaches 1.0 on the last frame; at 400 MPa the initiation stage is the 34,000 cycles of Session 1.

**Difficulty:** advanced

## The final step

Combine the milestones: a complete life estimate for a notched part under a measured load history, with initiation, crack growth, scatter and an inspection plan, and an animation that tells the story like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it.
