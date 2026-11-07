# Roadmap: the path to the opentrafficsignal Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: The random delay term

**You will learn:** Why random arrivals add delay on top of the uniform term, and how Webster's and Kimber-Hollis' formulas model it.

**You will build:** A formula for the total average delay that combines the uniform term and a random term, validated against the simulator.

**Checkpoint (not met by the shipped code):** Predicted average delay within 15 percent of the Poisson simulation for degrees of saturation between 0.5 and 0.9 (the shipped uniform term alone is 29 percent too low at x = 0.89: 13.86 s against 19.50 s).

**Difficulty:** intermediate

## Session 5: Adaptive timing for a swinging rush hour

**You will learn:** Time-varying demand, detector logic and how to judge a controller fairly against a fixed plan.

**You will build:** A simulator with demand that changes every few minutes and a smarter adaptive rule (for example one that compares queue pressure of both phases).

**Checkpoint (not met by the shipped code):** Over one hour of north-south and east-west demand swapping between 0.30 and 0.06 cars per second every 150 s, average delay at least 15 percent below the shipped actuated rule (which gives 10.0 s, with a largest queue of 14.6 cars) and a largest queue below 10 cars.

**Difficulty:** advanced

## Session 6: Three phases: a protected turn

**You will learn:** Lost time per phase, flow ratios for turning movements and Webster's cycle with three phases.

**You will build:** A controller and simulator with three phases (the shipped one supports two).

**Checkpoint (not met by the shipped code):** For critical flow ratios 0.30, 0.25 and 0.15 (Y = 0.70) and lost time 9 s, conservation holds and the simulated best cycle (scanned from 30 s to 150 s) lies within 20 percent of the formula value 61.7 s.

**Difficulty:** advanced

## Session 7: A green wave between two junctions

**You will learn:** Offsets, platoons and how a queue at one junction becomes the arrivals of the next.

**You will build:** Two signals 400 m apart, cars travelling at 10 m/s, linked by an offset.

**Checkpoint (not met by the shipped code):** With a 60 s cycle at both junctions, the best offset lets at most 20 percent of the cars stop at the second junction, while the worst offset makes at least three times as many stop.

**Difficulty:** advanced

## Session 8: Fit the model to real counts

**You will learn:** How to estimate arrival rates and saturation flow from a video or count sheet, and how far to trust a fit.

**You will build:** A script that reads counts per minute from a CSV, estimates q and s and reports predicted delay and queue.

**Checkpoint (not met by the shipped code):** On a 15-minute count you record yourself, the predicted largest queue is within 3 cars of the observed one and the predicted average delay within 25 percent.

**Difficulty:** intermediate

## The final step

Combine the milestones: a two-junction corridor with a swinging rush hour, three phases at the main junction, a random-delay prediction you can trust, and an adaptive rule that beats a good fixed plan. If your result looks like the Target animation, open a pull request and tell us how you did it.
