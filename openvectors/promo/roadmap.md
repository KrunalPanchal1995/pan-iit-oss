# Roadmap: the path to the openvectors Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A look-ahead heading controller

**You will learn:** How to predict the landing point of a held heading and re-aim every step, instead of reacting to the error.

**You will build:** A controller that, each step, picks the heading for which holding it to the far bank would land on the target line.

**Checkpoint (not met by the shipped code):** Land within 1 m in at most 25 s for a 4 m/s boat, a 4 m/s peak current and a 0.5 m/s wind (the shipped feedback pilot, over every gain from 0.5 to 8, gets no closer than 6.0 m).

**Difficulty:** advanced

## Session 5: A pilot that does not know the wind

**You will learn:** How a controller estimates a hidden disturbance from its own measured motion.

**You will build:** A wind estimator built from the difference between the measured ground arrow and the arrow the model predicts.

**Checkpoint (not met by the shipped code):** Land within 0.5 m for every wind in {-1, -0.5, 0, 0.5, 1} m/s with a 3 m/s peak current, using one fixed set of settings (the shipped pilot's best single gain still misses by about 1.06 m in the worst wind).

**Difficulty:** advanced

## Session 6: Follow a river bend

**You will learn:** Using vector components along and across a curved centre line instead of fixed x and y axes.

**You will build:** A simulation where the current follows a 90 degree bend of radius 150 m and the target line is the centre line.

**Checkpoint (not met by the shipped code):** Cross-track error below 2 m along the whole bend (the shipped simulation only handles a straight river).

**Difficulty:** advanced

## Session 7: Force systems: a tug and a barge

**You will learn:** Adding several force arrows, finding the resultant, and the torque on the tow rope.

**You will build:** A two-tug model where each tug pulls with a force arrow and the barge follows the resultant.

**Checkpoint (not met by the shipped code):** Two tugs whose forces (in newtons) sum to a resultant along the channel within 1 degree while the sideways force is below 5 percent of the total.

**Difficulty:** intermediate

## Session 8: Animate the crossing with arrows

**You will learn:** Drawing vectors on an animation frame by frame.

**You will build:** A GIF of the crossing with the boat, current and ground arrows drawn on the boat.

**Checkpoint (not met by the shipped code):** At least 40 frames, three arrow colours with a legend, and a file under 3 MB.

**Difficulty:** intermediate

## The final step

Combine the milestones: a ferry pilot that estimates the wind, looks ahead, and lands on the target line in a river with a bend, drawn with its arrows in an animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
