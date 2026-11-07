# Roadmap: the path to the openpipeflow Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Colebrook-White friction factor

**You will learn:** Why the exact friction equation needs iteration, and how to solve it quickly and safely.

**You will build:** A friction factor function that replaces the Swamee-Jain formula inside the network solver.

**Checkpoint (not met by the shipped code):** Agreement with a high-accuracy reference to 0.3 percent for Re from 5000 to 1e8 and e/D from 1e-6 to 5e-2 (the shipped formula is off by up to 2.8 percent).

**Difficulty:** intermediate

## Session 5: A general network solver

**You will learn:** Writing nodes and pipes as data and solving every loop at once with a Newton method on the node heads.

**You will build:** A solver that reads any list of pipes, nodes and demands.

**Checkpoint (not met by the shipped code):** A network of 8 pipes and 3 loops solved with node balance below 1e-9 m^3/s and loop closure below 1e-6 m (the shipped solver handles exactly one loop).

**Difficulty:** advanced

## Session 6: Pumps and tanks as network parts

**You will learn:** Pump curves, system curves and the operating point where they meet.

**You will build:** A pump element with a head-flow curve added to the network.

**Checkpoint (not met by the shipped code):** The reported operating point lies within 1 percent of the intersection of the pump curve and the system curve (the shipped code has no pump curve).

**Difficulty:** advanced

## Session 7: A day of demand

**You will learn:** Time-varying demand and a tank that fills and empties.

**You will build:** A 24-hour simulation with a demand pattern and a tank level.

**Checkpoint (not met by the shipped code):** A 24-hour run in which the tank never empties and no node falls below 20 m at any hour (the shipped steady model has no time at all).

**Difficulty:** advanced

## Session 8: Draw the town

**You will learn:** Turning a solved network into a picture: pipe widths, flow arrows and a pressure colour scale.

**You will build:** A map with moving flow dots and node colours.

**Checkpoint (not met by the shipped code):** An animation of at least 24 frames of a 12-node town that reproduces the solver's pressures to the colour-scale resolution.

**Difficulty:** intermediate

## The final step

Combine the milestones: a general network solver with pumps, a tank and a daily demand cycle, drawn as an animated map. If your result looks like the Target animation, open a pull request and tell us how you did it.
