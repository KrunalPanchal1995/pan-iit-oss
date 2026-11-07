# Roadmap: the path to the openfoundation Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Neighbouring footings and overlapping bulbs

**You will learn:** How the stress from two footings adds at a point between them, using the closed-form stress under a loaded rectangle.

**You will build:** A function giving the added vertical stress at any point (x, y, z) from several rectangular footings.

**Checkpoint (not met by the shipped code):** The added stress at 3 m depth midway between two 2 m square footings of 150 kPa, centres 4 m apart, is 25.4 kPa within 0.3 kPa (the shipped code only handles a point under the centre of one footing).

**Difficulty:** intermediate

## Session 5: Staged loading in time

**You will learn:** Superposition of consolidation curves when the load is applied in steps.

**You will build:** A settlement-time function for a load applied half at time zero and half after one year.

**Checkpoint (not met by the shipped code):** The consolidation settlement at 2 years for the worked clay layer (c_v 1.5 m2/year, H_dr 2 m, final 86.4 mm in the Session 3 app case) is 67.0 mm within 1 mm (the shipped one-shot code gives 75.4 mm).

**Difficulty:** intermediate

## Session 6: A combined footing for two columns

**You will learn:** Putting two columns on one rectangular footing so that the resultant is in the middle third.

**You will build:** A search over the width of a 4 m long footing carrying 600 kN and 300 kN columns 3 m apart, each 0.5 m from the nearest end.

**Checkpoint (not met by the shipped code):** The smallest width in 0.05 m steps with no tension and a peak contact pressure plus footing weight (0.6 m thick) of at most 150 kPa is 2.95 m (the shipped code treats one column at a time).

**Difficulty:** intermediate

## Session 7: Uncertain soil strength

**You will learn:** Treating cohesion as a random variable and turning a factor of safety into a probability of failure.

**You will build:** A Monte Carlo run of 200000 samples of a lognormal cohesion with mean 50 kPa and 30 percent coefficient of variation under a strip footing pressure of 114.4 kPa.

**Checkpoint (not met by the shipped code):** The estimated probability that 5.7 c is below the applied pressure lies between 0.10 and 0.25 percent (the shipped code gives a single deterministic factor of safety of 2.49).

**Difficulty:** advanced

## The final step

Combine the milestones: a footing loaded in steps on a clay layer, with the exact pressure bulb of the neighbouring footings, a settlement-time curve and a bearing check. If your result looks like the Target animation, open a pull request and tell us how you did it. Remember that all of this is a classroom model and never a method for designing a real foundation.
