# Roadmap: the path to the openevacuation Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: People are not all the same

**You will learn:** Why fire engineers describe pre-movement times and walking speeds as distributions, and why a design value is a high percentile, not the average.

**You will build:** Pre-movement times (for example lognormal) and walking speeds drawn per person or per group, released into the Session 3 network, and a Monte Carlo of 500 runs that reports the mean and the 95th-percentile evacuation time.

**Checkpoint (not met by the shipped code):** When every person gets the same pre-movement time of 60 s, every run reproduces the shipped 482.5 s for the one-stair block; with a spread, the report prints a 95th percentile and a histogram (the shipped code has a single fixed start time).

**Difficulty:** intermediate

## Session 5: Draw the floor plan

**You will learn:** How to describe rooms, corridors, doors and stairs as a graph, and how people choose an exit by the shortest route.

**You will build:** A reader for a small text file of nodes and links (width, length, kind), shortest-route exit choice (Dijkstra), and the Session 3 simulation running on that graph.

**Checkpoint (not met by the shipped code):** A plan file that describes the shipped four-storey block gives the same 482.5 s, and moving one stair door to the far end of a 40 m corridor makes the simulation route people to the other stair (the shipped code only splits floors equally).

**Difficulty:** intermediate

## Session 6: Counterflow and merging rules

**You will learn:** How firefighters climbing a stair and the rule for who goes first on a landing change the flow.

**You will build:** A lane of the stair reserved for counterflow (a reduced effective width) and three merging rules on landings: first come, floor priority, and taking turns.

**Checkpoint (not met by the shipped code):** All three merging rules give the same total evacuation time within 2 percent when the stair is the only bottleneck (conservation through the bottleneck), but different waiting times per floor; reserving a 0.5 m lane lengthens the evacuation in proportion to the lost effective width.

**Difficulty:** intermediate

## Session 7: People as agents

**You will learn:** The social-force model, in which each person is pushed towards the exit and away from walls and from each other.

**You will build:** A 2D simulation of individuals leaving a room through one door, with a few hundred agents and simple time stepping.

**Checkpoint (not met by the shipped code):** For a 1.2 m door the measured flow of agents lies within 25 percent of the hydraulic value of Session 1 (1.17 persons/s), and the measured speed-density points fall near the Session 2 line (the shipped code has no individuals).

**Difficulty:** advanced

## Session 8: Smoke and ASET

**You will learn:** How a fire fills a room with smoke, how ASET is estimated, and how smoke slows people.

**You will build:** A two-zone smoke-filling model that gives the time until the smoke layer reaches 2 m (ASET), and a walking speed that falls inside smoke.

**Checkpoint (not met by the shipped code):** A larger fire gives a shorter ASET, and the RSET of a route through smoke is longer than the same route without it (the shipped code takes ASET as a given number).

**Difficulty:** advanced

## The final step

Combine the milestones: a floor plan you can draw, people with spread-out start times and speeds, exit choice, smoke-limited ASET and an agent animation, with a report of RSET against ASET for every design. If your tool reproduces the Target bars and goes beyond them, open a pull request and tell us how you did it.
