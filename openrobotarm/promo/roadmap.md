# Roadmap: the path to the openrobotarm Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Whole-arm collision checking

**You will learn:** Distances from line segments (the links) to obstacles, and planning when the arm itself must keep clear.

**You will build:** A checker that tests every link of the arm, not just the gripper, against the no-go zone, and a planner that picks the route and the elbow choice.

**Checkpoint (not met by the shipped code):** Every link keeps at least 0.03 m clearance from the edge of the radius 0.06 m zone along the whole pick-and-place (the shipped route lets a link pass inside the zone).

**Difficulty:** intermediate

## Session 5: Speed limits and time-optimal timing

**You will learn:** Joint speed and acceleration limits, and how timing along a path is chosen.

**You will build:** A planner that stretches the move in time until no joint exceeds a speed limit.

**Checkpoint (not met by the shipped code):** A 0.60 m move with every joint at or below 1.5 rad/s (the shipped 2 s path peaks at 2.42 rad/s in one joint).

**Difficulty:** intermediate

## Session 6: Calibrate the link lengths

**You will learn:** Fitting model parameters to measurements by least squares.

**You will build:** A program that recovers the true link lengths from measured gripper positions at several poses.

**Checkpoint (not met by the shipped code):** Recover link lengths that are wrong by 1 mm each to within 0.1 mm (the nominal model is off by 2.005 mm at the pose for (0.45, 0.20) m).

**Difficulty:** advanced

## Session 7: A six-joint arm in 3D with orientation

**You will learn:** Rotation matrices in 3D, the Denavit-Hartenberg convention and a 6 x 6 Jacobian.

**You will build:** Forward and numerical inverse kinematics for a six-joint arm that sets position and orientation.

**Checkpoint (not met by the shipped code):** Position error below 1e-6 m and orientation error below 1e-6 rad on 100 random reachable poses (the shipped code only handles 2D position).

**Difficulty:** advanced

## Session 8: Animate the pick-and-place

**You will learn:** Putting kinematics, timing and drawing together into an animation.

**You will build:** A looping animation of pick, carry, place and return, exported as a GIF, with the swept workspace and joint traces.

**Checkpoint (not met by the shipped code):** A closed loop whose first and last frames differ by less than 1e-6 in every joint angle and a file under 3 MB.

**Difficulty:** advanced

## The final step

Combine the milestones: a six-joint arm that plans a collision-free, speed-limited pick-and-place, calibrated from measurements, with a clean exported animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
