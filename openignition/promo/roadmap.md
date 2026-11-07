# Roadmap: the path to the openignition Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A chain-branching toy with an explosion limit

**You will learn:** How radicals multiply (branching) and are destroyed on walls or in three-body collisions (termination), and why that creates pressure limits.

**You will build:** A three-variable toy (fuel, a radical pool, temperature) whose delay depends on pressure in a non-monotone way.

**Checkpoint (not met by the shipped code):** Below a limit pressure the mixture does not ignite at all (delay infinite) at a fixed start temperature; the shipped one-step toy still ignites at 0.1 atm with a delay of 11.9 ms.

**Difficulty:** intermediate

## Session 5: Variable heat capacity

**You will learn:** Why the temperature rise is not a constant: cp grows with temperature, so the burnt gas ends cooler.

**You will build:** A reactor with a temperature-dependent cp (a simple polynomial) in place of the constant DT_AD.

**Checkpoint (not met by the shipped code):** With cp rising by 30 percent between 1000 K and 2500 K, the final temperature from a 1000 K start is at least 150 K below the 2500 K that the shipped constant-cp model gives.

**Difficulty:** intermediate

## Session 6: A higher-order stiff solver

**You will learn:** Rosenbrock or backward-differentiation methods, and how order lowers the step count at a tight tolerance.

**You will build:** An implicit solver of order three or more with an analytic Jacobian.

**Checkpoint (not met by the shipped code):** Delay error below 1e-6 with fewer than 100 accepted steps to reach 30 ms (the shipped trapezoid needs 457 steps for 1e-6).

**Difficulty:** advanced

## Session 7: Include fuel burn-up in the Semenov boundary

**You will learn:** Why the analytic criterion is a lower bound and how to correct it.

**You will build:** A modified criterion or a quick numerical correction for the critical surrounding temperature.

**Checkpoint (not met by the shipped code):** Predict the simulated critical temperature 924.7 K at a loss rate of 500 per second to within 3 K (the shipped analytic criterion gives 905.7 K).

**Difficulty:** advanced

## Session 8: Hot-spot ignition in one dimension

**You will learn:** Reaction-diffusion: a small hot patch either cools down or ignites a flame kernel, as in the PANSOPHIA hot-spot figure.

**You will build:** A one-dimensional grid with heat conduction added to the toy reaction.

**Checkpoint (not met by the shipped code):** The critical hot-spot width changes by less than 2 percent when the grid spacing is halved.

**Difficulty:** advanced

## The final step

Combine the milestones: a chain-branching reactor with variable heat capacity, a stiff solver with fewer than 100 steps, and a map of ignition delay over temperature and pressure with its no-ignition region. If your result looks like the Target animation, open a pull request and tell us how you did it.
