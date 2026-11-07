# Activity sheet: openrobotarm, Session 2: Where can the gripper go? Workspace, joint limits and redundancy

Name: ____________________   Date: ____________

**Objectives**

- Describe the workspace of two links as a ring and measure an area by sampling a grid.
- Explain how a third link and the tool direction fill the workspace, and how joint limits cut it.
- Compute the reachable fraction of the workspace for given joint limits.
- Explain redundancy: one target, many arm shapes.
- Choose link lengths and joint limits so a work table is fully reachable.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the joint angles that put the gripper at (0.45, 0.20) m pointing along +x (phi = 0), for L = (0.30, 0.25, 0.15) m. Are they within +-120 degrees?

1. ______________________________  (hint: Wrist: w = (0.45, 0.20) - 0.15 * (1, 0) = (0.30, 0.20) m, so |w|^2 = 0...)
2. ______________________________  (hint: cos q2 = (0.13 - 0.0900 - 0.0625) / (2 * 0.30 * 0.25) = -0.0225 / 0.15...)
3. ______________________________  (hint: For q2 = +98.63: atan2(0.20, 0.30) = 33.69 degrees and atan2(0.25 * 0....)
4. ______________________________  (hint: Then q3 = 0 - (-9.59) - 98.63 = -89.04 degrees. The other elbow choice...)
5. ______________________________  (hint: All six angles have magnitude below 120 degrees, so both shapes are al...)

Final answer: ____________________

## Questions
**A. Conceptual.** A two-link arm with L1 = 0.30 m and L2 = 0.25 m has a hole of radius 0.05 m in its workspace. Why does adding a 0.15 m third link remove the hole, if the gripper's direction is free?

Answer: ______________________________________________


**B. Numerical.** Compute the reachable area of a two-link arm with L1 = 0.40 m and L2 = 0.20 m, and its smallest and largest radius.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the graph of reachable fraction against joint limit, with L = (0.30, 0.25, 0.15) m, how much of the disk is lost at +-90 degrees, and what is the smallest 5 degree step of the limit that keeps 90 percent?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a work table 0.5 m x 0.3 m has its short edge 0.20 m in front of the base, centred on it. Choose L3 (keeping L1 = 0.30 m and L2 = 0.25 m) and the smallest joint limit in 5 degree steps so every point of the table is reachable. Justify it.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
