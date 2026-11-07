# Roadmap: the path to the opentolerance Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Parts that are not normal

**You will learn:** How uniform or skewed part distributions change the tail of the gap, and why RSS is still right for the sigma.

**You will build:** A stack simulator that draws each part from a normal, a uniform or a skewed distribution.

**Checkpoint (not met by the shipped code):** For uniform parts of half-width t, the simulated gap sigma matches sqrt(sum t_i^2 / 3) within 1 percent, and the out-of-tolerance fraction is smaller than the normal-model value.

**Difficulty:** intermediate

## Session 5: Watch for drift with a control chart

**You will learn:** How an X-bar control chart detects a drifting process centre before the assemblies fail.

**You will build:** A control chart with three-sigma limits on subgroups of five, driven by a slowly drifting simulated process.

**Checkpoint (not met by the shipped code):** A one-sigma drift of the process is flagged within 20 subgroups in at least 90 percent of 1000 simulated runs (the shipped code, which has no chart, flags none).

**Difficulty:** intermediate

## Session 6: Allocate with standard IT grades

**You will learn:** Real drawings use standard tolerance grades, not any value; allocation then becomes a discrete choice.

**You will build:** An allocator that picks an IT grade for each part from a table and minimises the illustrative cost.

**Checkpoint (not met by the shipped code):** Every tolerance is a table value, the gap meets Cp 1.33 and the total cost is within 10 percent of the continuous optimum 44.94 (the shipped allocation uses non-standard values such as 0.0608 mm).

**Difficulty:** advanced

## Session 7: Design that survives drift

**You will learn:** Choosing tolerances and capability so that a one-sigma drift does not ruin the yield.

**You will build:** A design search that adds a drift allowance and reports the cheapest allocation that still passes.

**Checkpoint (not met by the shipped code):** With every process drifted by one sigma, less than 0.5 percent of assemblies fail (the shipped allocation fails about 3.1 percent).

**Difficulty:** advanced

## Session 8: Stacks in two dimensions

**You will learn:** Vector loops and sensitivity coefficients when parts are not in a straight line.

**You will build:** A stack where one part is tilted, with each tolerance weighted by the sine or cosine of its angle.

**Checkpoint (not met by the shipped code):** The simulated gap sigma matches the sensitivity-weighted RSS within 1 percent for three tilt angles.

**Difficulty:** advanced

## The final step

Combine the milestones: a tolerance simulator that draws parts from real-looking distributions, picks standard IT grades at minimum cost, watches the process with a control chart and reports the yield under drift, with a clean animation. If your result looks like the Target, open a pull request and tell us how you did it.
