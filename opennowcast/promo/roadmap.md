# Roadmap: the path to the opennowcast Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Growth-aware advection

**You will learn:** How to measure the growth or decay of each region between two frames and carry it along with the motion.

**You will build:** A forecast that advects the field and multiplies it by a growth map that is itself advected.

**Checkpoint (not met by the shipped code):** CSI of at least 0.6 at 60 minutes and 10 mm/h on the GROWTH scene (the shipped local forecast gives 0.38).

**Difficulty:** intermediate

## Session 5: Follow the rotation

**You will learn:** Why a straight-line shift fails for a rotating pattern and how updating the motion in small steps along a curved path helps.

**You will build:** A forecast that advects in several sub-steps using the vectors at each new position.

**Checkpoint (not met by the shipped code):** CSI of at least 0.5 at 60 minutes on the rotating-ring scene (the shipped local forecast gives 0.08).

**Difficulty:** advanced

## Session 6: Sharper long steps

**You will learn:** Numerical diffusion and higher-order interpolation (cubic) or accumulating the displacement before interpolating.

**You will build:** A stepping scheme that moves a cell for 60 minutes in 12 steps without smoothing it.

**Checkpoint (not met by the shipped code):** A 30 mm/h cell of width 2.5 pixels keeps a peak of at least 29.5 mm/h after 12 steps (the shipped repeated steps give 24.99).

**Difficulty:** intermediate

## Session 7: Reliable at every confidence level

**You will learn:** Calibrating an ensemble: choosing the spread of the wind errors from past errors.

**You will build:** A probability forecast whose reliability table lies near the diagonal in every bin.

**Checkpoint (not met by the shipped code):** A gap between forecast probability and observed frequency of less than 0.05 in every bin with more than 1000 pixels (the shipped ensemble has a gap of 0.12 in its highest bin).

**Difficulty:** advanced

## Session 8: Storm initiation hints

**You will learn:** What information (terrain, convergence lines, satellite) predicts new storms that radar cannot yet see.

**You will build:** A rule that flags areas of likely initiation and a way to score it.

**Checkpoint (not met by the shipped code):** At least 50 of the 193 rainy pixels of the new storm in the failure-case scene are flagged at 60 minutes (the shipped forecast flags 0).

**Difficulty:** advanced

## The final step

Combine the milestones: a nowcast with local flow, growth and decay, a curved-path scheme and a calibrated probability map, validated on synthetic scenes and then on a real radar archive. If your result looks like the Target animation, open a pull request and tell us how you did it. Remember that this is a teaching project, not a weather warning system.
