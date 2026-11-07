# Roadmap: the path to the openvfx Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Helper bones at the elbow

**You will learn:** How real rigs add an extra joint so the elbow keeps its width.

**You will build:** A three-bone arm (upper arm, helper, forearm) skinned with weights.

**Checkpoint (not met by the shipped code):** Elbow width ratio of at least 0.85 at a 120 degree bend with the largest gap below 0.1 (the shipped skin gives 0.50).

**Difficulty:** intermediate

## Session 5: Paint the weights

**You will learn:** Weights as data you can edit, and how artists tune them point by point.

**You will build:** A small weight editor with a sliders-per-region interface that reports gap and width.

**Checkpoint (not met by the shipped code):** A weight set that gives width ratio of at least 0.75 and gap below 0.08 at a 90 degree bend (the shipped skin gives 0.707).

**Difficulty:** intermediate

## Session 6: Blend rotations, not matrices (2D)

**You will learn:** Why averaging matrices shrinks shapes, and what quantity can be averaged safely.

**You will build:** A second skinning function with constant width along the arm.

**Checkpoint (not met by the shipped code):** Width ratio of at least 0.99 for every bend up to 150 degrees (the shipped skin gives 0.26 at 150).

**Difficulty:** advanced

## Session 7: Go 3D: twist and quaternions

**You will learn:** Quaternions as rotations you can blend safely, and why twist is harder than bend.

**You will build:** The same arm in 3D with a twisting forearm.

**Checkpoint (not met by the shipped code):** A 180 degree forearm twist keeps the minimum radius of the skin at 0.9 of the rest radius or more.

**Difficulty:** advanced

## Session 8: Animate a wave cycle

**You will learn:** Keyframes and interpolation of joint angles over time.

**You will build:** A looping animation exported as a GIF.

**Checkpoint (not met by the shipped code):** A 2 second loop at 24 frames per second whose first and last frames differ by less than 1e-6.

**Difficulty:** advanced

## The final step

Combine the milestones: a four-bone arm that waves in 3D, with a skin that keeps its width and a clean exported animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
