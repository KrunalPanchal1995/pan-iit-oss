# Roadmap: the path to the opentruss Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Moving loads and influence lines

**You will learn:** How the force in one bar changes as a single load rolls along the deck, and why the worst case is not the midspan case.

**You will build:** A function that places a load at any position on the deck (shared linearly between the two neighbouring deck joints) and returns the force envelope of every bar.

**Checkpoint (not met by the shipped code):** For the 12 m Pratt truss (6 panels, 2 m high) and a rolling 20 kN load, the diagonal that runs from the top joint above x = 2 m down to the bottom joint at x = 4 m reaches an absolute force of at least 18.8 kN (the shipped midspan-only analysis gives 14.1 kN).

**Difficulty:** intermediate

## Session 5: Buckling-aware sizing

**You will learn:** Hollow tubes, second moment of area and Euler buckling as a sizing constraint.

**You will build:** A sizing routine that gives compression bars a tube section and checks them against the Euler load with a safety factor.

**Checkpoint (not met by the shipped code):** Every compression bar of the 12 m Pratt footbridge design has an Euler load of at least twice its force (the shipped solid-round-bar sizing passes for 0 of its 8 compression bars).

**Difficulty:** intermediate

## Session 6: Optimal sizing from virtual work

**You will learn:** Choosing each bar's area to meet a deflection limit with the least material, instead of scaling everything together.

**You will build:** A sizing routine that minimises mass for a sag limit using the unit-load formula and bounds on area.

**Checkpoint (not met by the shipped code):** The 12 m Pratt footbridge meets the 15 mm limit with a mass of at most 108 kg (the shipped sizing gives 111 kg).

**Difficulty:** advanced

## Session 7: Self-weight and load cases

**You will learn:** Adding the bars' own weight to the joint loads, and iterating because heavier bars weigh more.

**You will build:** A loop that recomputes the sizing with the self-weight of the bars shared between their end joints.

**Checkpoint (not met by the shipped code):** The Pratt footbridge mass at the 15 mm limit converges to within 0.01 kg after a few iterations, near 112.8 kg (the shipped design ignoring self-weight gives 111 kg).

**Difficulty:** intermediate

## Session 8: Go 3D: a space truss

**You will learn:** Direction cosines in three dimensions and a 3 by 3 block per joint.

**You will build:** The same stiffness solver for space trusses, tested on a three-legged tower (tripod).

**Checkpoint (not met by the shipped code):** A tripod whose joints on the ground form a circle of radius 1 m, apex 3 m high, carrying 12 kN, has each leg in compression of 4.22 kN.

**Difficulty:** advanced

## The final step

Combine the milestones: a rolling load on a truss whose members are sized for strength, deflection and buckling, drawn with bars coloured by force and the deflected shape exaggerated. If your result looks like the Target animation, open a pull request and tell us how you did it.
