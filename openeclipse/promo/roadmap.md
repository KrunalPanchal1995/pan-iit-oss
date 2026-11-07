# Roadmap: the path to the openeclipse Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Minute-level timing

**You will learn:** Where the remaining error of a short series comes from, and how more terms of the Moon's motion remove it.

**You will build:** A longer series for the new moon time and the Moon's latitude, checked against published eclipses.

**Checkpoint (not met by the shipped code):** The largest timing error over the 13 published eclipses is under 5 minutes (the shipped model's largest error is 11.8 minutes).

**Difficulty:** intermediate

## Session 5: Every type right

**You will learn:** How the Earth's flattening and the hybrid case change the verdict near a boundary.

**You will build:** An improved classifier for total, hybrid, annular and partial eclipses.

**Checkpoint (not met by the shipped code):** All 13 types are correct and the largest gamma error is 0.01 Earth radii or less (the shipped model gets 11 of 13 and 0.034).

**Difficulty:** intermediate

## Session 6: The footprint on a rotating Earth

**You will learn:** How to place the shadow axis on a rotating sphere and turn it into latitude and longitude.

**You will build:** A simulation of the umbra footprint for one eclipse, drawn on a world outline.

**Checkpoint (not met by the shipped code):** Simulating two Saros partners gives a longitude difference between 110 and 125 degrees (the shipped code only has the formula, no footprint).

**Difficulty:** advanced

## Session 7: Build a whole Saros series

**You will learn:** How the geometry creeps from one eclipse to the next and why a series starts and ends.

**You will build:** A listing of every member of one series with its type, gamma and magnitude.

**Checkpoint (not met by the shipped code):** The series is built member by member, gamma changes in one direction at every step, and its true length is reported (the shipped code only estimates 69 from a formula).

**Difficulty:** advanced

## Session 8: Lunar eclipses as the other half

**You will learn:** The Earth's dark shadow at the Moon (4606 km radius) and why lunar eclipses come two weeks from solar ones.

**You will build:** A predictor for lunar eclipses in the same 3-year window.

**Checkpoint (not met by the shipped code):** Every predicted lunar eclipse lies about half a synodic month from a new moon that is in an eclipse season.

**Difficulty:** advanced

## The final step

Combine the milestones: an animated Sun, Moon and Earth with shadow cones, a Moon that crosses its node, a footprint on a world outline, and a Saros series whose tracks step west. If your result looks like the Target animation, open a pull request and tell us how you did it. Never look at the Sun without certified eclipse glasses.
