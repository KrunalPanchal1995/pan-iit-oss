# Roadmap: the path to the openlinkage Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Make the leg mountable

**You will learn:** A leg must also fit under a body: every pin has to stay above the ground line while the stance line is level.

**You will build:** A search over ground, coupler, rocker and foot position that includes the lowest-pin height in the requirement list.

**Checkpoint (not met by the shipped code):** A leg with no dig, lift at least 15 percent of the stride, smallest transmission angle at least 40 degrees, lowest pin at or above the stance line and stance deviation at most 6 percent of the stride (our leg has its lowest pin 1.06 below the line and the tuned leg 1.36 below).

**Difficulty:** intermediate

## Session 5: Walk at a steady speed

**You will learn:** Why the foot nearly stops at both ends of the stance and how bar proportions even out the ground speed.

**You will build:** A speed-uniformity measure along the stance added to the leg search.

**Checkpoint (not met by the shipped code):** Foot speed along the stance with (fastest minus slowest) / mean at most 2.0 while the deviation stays below 4 percent of the stride (our leg gives 2.21 and 7.74 percent).

**Difficulty:** intermediate

## Session 6: Many legs, one gait

**You will learn:** Phase offsets between cranks and the duty factor: how many feet are on the ground at once.

**You will build:** A multi-leg walker model with a phase offset for each leg.

**Checkpoint (not met by the shipped code):** A six-leg walker whose crank phases alternate by 180 degrees keeps at least 3 feet on the ground at every instant (the shipped code simulates one leg only).

**Difficulty:** intermediate

## Session 7: Tolerance budget

**You will learn:** Turn the sensitivity study into a tolerance specification for building the leg: the tuned leg sits next to a cliff.

**You will build:** A Monte Carlo study of random bar-length errors.

**Checkpoint (not met by the shipped code):** With every bar length and the foot position randomly wrong by up to 3 percent, at least 95 percent of 1000 trial legs show no dig (the tuned leg of Session 3 falls short of 93 percent).

**Difficulty:** advanced

## Session 8: Go beyond four bars

**You will learn:** Why walkers such as Jansen's use eight or more bars: more links allow a much flatter stance together with a swing on the body side.

**You will build:** A six- or eight-bar leg solved with the same circle-circle method.

**Checkpoint (not met by the shipped code):** A mountable leg with no dig, lift at least 15 percent of the stride and stance deviation at most 0.7 percent of the stride (the best mountable four-bar leg of our search gives about 5.3 percent).

**Difficulty:** advanced

## The final step

Combine the milestones: a multi-legged walker whose legs are tuned, phased and built within a tolerance budget, with a body that moves steadily over the ground. If your result looks like the Target animation, open a pull request and tell us how you did it.
