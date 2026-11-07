# Roadmap: the path to the openmole Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Equations with many solutions

**You will learn:** Why some equations have a cone of positive solutions, and how to list its extreme recipes.

**You will build:** A balancer that, for nullity 2 or more, returns the extreme positive integer solutions instead of just a basis.

**Checkpoint (not met by the shipped code):** For C3H8 + O2 -> CO2 + CO + H2O return exactly the two extreme recipes (1, 5, 3, 0, 4) and (2, 7, 0, 6, 8); the shipped balancer returns only a basis that contains negative entries.

**Difficulty:** intermediate

## Session 5: Titration: from volumes to a concentration

**You will learn:** Solution stoichiometry with a measured end point, averaging and spread.

**You will build:** A calculator that turns titration volumes into a concentration with an uncertainty.

**Checkpoint (not met by the shipped code):** From 24.6, 24.8 and 24.7 mL of 0.100 mol/L NaOH neutralising 25.0 mL of H2SO4 (H2SO4 + 2 NaOH -> Na2SO4 + 2 H2O) report 0.0494 mol/L within 0.0003, with the spread of the three readings.

**Difficulty:** intermediate

## Session 6: Recycle and purge

**You will learn:** Per-pass conversion versus overall conversion in a loop with a purge.

**You will build:** A steady-state mass balance of a reactor, separator and recycle stream.

**Checkpoint (not met by the shipped code):** With 15 percent per-pass conversion of N2, show that an overall N2 conversion of at least 97 percent needs a purge of at most 0.5 percent of the recycle (the shipped single-pass reactor reaches only 15 percent).

**Difficulty:** advanced

## Session 7: Equilibrium instead of complete reactions

**You will learn:** Equilibrium constants and solving for the extent numerically.

**You will build:** A solver for the equilibrium extent of a reaction with a given constant.

**Checkpoint (not met by the shipped code):** For the toy reaction 2A <-> B in 1 L with K = 4 (concentrations in mol/L) starting from 1 mol of A, find the extent 0.352 mol (the shipped complete-reaction model gives 0.500 mol).

**Difficulty:** advanced

## Session 8: Animate the balancer

**You will learn:** Mapping atoms between reactant and product molecules and animating the regrouping.

**You will build:** An animation of any balanced reaction with mole and mass bars.

**Checkpoint (not met by the shipped code):** A 48-frame animation in which the total mass bar stays within 1e-9 of its starting value in every frame.

**Difficulty:** advanced

## The final step

Combine the milestones: a balancer that handles many-solution equations, a reactor with recycle and equilibrium, and an animation that shows the atoms regrouping with the mass bars staying constant. If your result looks like the Target animation, open a pull request and tell us how you did it.
