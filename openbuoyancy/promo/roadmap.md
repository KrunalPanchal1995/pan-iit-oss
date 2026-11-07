# Roadmap: the path to the openbuoyancy Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 5: A round-bilge hull

**You will learn:** Stability of a section that is not a box: general polygons, clipping and centroids.

**You will build:** A generalised wet-section function for any polygon hull, with the GZ curve plotted.

**Checkpoint (not met by the shipped code):** The GZ curve of a hull with rounded bilges agrees with an independent fine-grid area calculation to within 2 mm at every heel angle (the shipped code accepts only a rectangle).

**Difficulty:** intermediate

## Session 6: Roll in time

**You will learn:** Natural roll period and what GM does to it; equation of motion for rolling with damping.

**You will build:** A time-stepping model of rolling that uses the GZ curve as the restoring moment.

**Checkpoint (not met by the shipped code):** For a radius of gyration of 2.1 m and GM = 0.75 m the simulated period is within 3 percent of T = 2 pi k / sqrt(g GM), about 4.9 s (the shipped code has no motion at all).

**Difficulty:** advanced

## Session 7: Settle at the angle of loll

**You will learn:** How damping makes a vessel with negative GM find its angle of loll, and when it capsizes.

**You will build:** A dynamic simulation of the failure case with a small disturbance.

**Checkpoint (not met by the shipped code):** The 3.8 m cargo case settles within 0.5 degrees of the loll angle 19.0 degrees found by the static calculation (the shipped code finds it only statically).

**Difficulty:** advanced

## Session 8: A stability report for a loading plan

**You will learn:** How a loading condition is checked against several criteria at once, and how to present the results clearly.

**You will build:** A script that reads cargo items, finds KG, GM, the GZ curve and the area under it, and prints pass or fail.

**Checkpoint (not met by the shipped code):** For a list of five cargo items, the printed KG matches a hand calculation to 1 mm and the verdict agrees with the sign of GM.

**Difficulty:** advanced

## The final step

Combine the milestones: a ship section of your own design, with free-surface liquids and rolling in time, whose heeling animation shows G, B and M and the righting-arm area. If your result looks like the Target animation, open a pull request and tell us how you did it.
