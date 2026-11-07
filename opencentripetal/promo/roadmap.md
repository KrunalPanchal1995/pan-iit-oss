# Roadmap: the path to the opencentripetal Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 5: Weight transfer between left and right wheels

**You will learn:** Why the outer wheels carry more load in a bend, and what that does to the grip.

**You will build:** A car with centre of gravity height, track width and four tyre loads.

**Checkpoint (not met by the shipped code):** For a 1200 kg car, centre of gravity 0.55 m high, track 1.5 m, at 5 m/s^2 sideways, the outer pair of wheels carries 2200 N more than the inner pair (the shipped point mass has no wheels).

**Difficulty:** intermediate

## Session 6: Rollover before sliding

**You will learn:** Why tall vehicles tip over before they slide, with tip speed sqrt(g R t / (2 h)).

**You will build:** A rollover check added to the friction-circle limit.

**Checkpoint (not met by the shipped code):** For track 1.5 m, centre of gravity 0.9 m, mu = 1.1, R = 100 m, report a tip speed of 102.9 km/h that is below the slide speed of 118.3 km/h (the shipped code reports only the slide speed).

**Difficulty:** advanced

## Session 7: Plan the speed round a whole circuit

**You will learn:** Forward and backward passes that give the fastest speed profile allowed by the friction circle.

**You will build:** A speed planner for a stadium circuit of two 100 m straights and two half circles of radius 30 m.

**Checkpoint (not met by the shipped code):** A lap time below 21 s on dry road (mu 0.8); the shipped constant corner speed lap takes 25.3 s.

**Difficulty:** advanced

## Session 8: Measure mu and compare with a turntable

**You will learn:** How to measure a friction coefficient with a tilt test and test a prediction against a real experiment.

**You will build:** A short lab report with a measured mu, a predicted slip speed and a measured slip speed.

**Checkpoint (not met by the shipped code):** Predicted slip speed sqrt(mu g / r) within 10 percent of the measured one (for mu = 0.5 and r = 0.10 m the prediction is 66.9 revolutions per minute).

**Difficulty:** intermediate

## The final step

Combine the milestones: a car that follows a real circuit with transition spirals and banked corners, shares its tyre grip between braking and cornering, reports rollover and slide limits, and plans its speed. If your result looks like the Target animation, open a pull request and tell us how you did it.
