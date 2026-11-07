# Roadmap: the path to the openprojectile Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Bounce and roll

**You will learn:** How a ball bounces (restitution) and loses speed on grass, and how to continue a simulation after an event.

**You will build:** A flight that continues after the first landing with a bounce model (illustrative: vertical speed halved, horizontal speed times 0.8).

**Checkpoint (not met by the shipped code):** The 35 m/s, 40 degree shot from 1 m lands a second time at 104.9 m, within 0.5 m (the shipped code stops at the first landing, 83.5 m).

**Difficulty:** intermediate

## Session 5: Crosswind in 3D

**You will learn:** Extending the model to three dimensions with the drag force on the relative velocity vector.

**You will build:** A 3D version of the solver with a sideways wind.

**Checkpoint (not met by the shipped code):** With a 5 m/s crosswind the same shot drifts 5.2 m sideways (within 0.3 m) and lands 83.1 m along the pitch (the shipped 2D code has no sideways direction).

**Difficulty:** intermediate

## Session 6: Fit the drag coefficient from a video

**You will learn:** Inverse problems: tuning a model parameter so that the simulation matches noisy measurements.

**You will build:** A least-squares fit of Cd to simulated camera points (positions every 0.1 s with 0.2 m of noise).

**Checkpoint (not met by the shipped code):** Recover the true Cd = 0.4 to within 5 percent (the shipped code can only run forward).

**Difficulty:** advanced

## Session 7: The optimal-angle map, fast

**You will learn:** Vectorising a simulation so that thousands of shots run at once.

**You will build:** A map of the best angle over 26 launch speeds (10 to 60 m/s) and 21 drag coefficients (0 to 0.8).

**Checkpoint (not met by the shipped code):** The whole 546-point map in under 10 seconds on a laptop (the shipped `best_angle` takes about 0.5 s per point, roughly 4.5 minutes for the map).

**Difficulty:** advanced

## Session 8: A shot planner with uncertainty

**You will learn:** Turning a single answer into a range of outcomes when the inputs are uncertain.

**You will build:** A function that reports the lowest and highest range for Cd between 0.35 and 0.45 and wind between -3 and +3 m/s.

**Checkpoint (not met by the shipped code):** For a 32 m/s, 42 degree hit from 1 m report a band of about 66 m to 81 m around the single-number answer of 73.8 m (the shipped code returns one number).

**Difficulty:** advanced

## The final step

Combine the milestones: a planner that takes the rope distance, the wind and the ball, and returns a launch speed and angle with a margin, shown as an animated trajectory and an optimal-angle map. If your result looks like the Target animation, open a pull request and tell us how you did it.
