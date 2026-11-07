# Roadmap: the path to the openseasons Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A truer Moon calendar

**You will learn:** The main corrections to the Moon's mean motion (its speed changes round its orbit).

**You will build:** A phase calendar that adds the largest periodic terms.

**Checkpoint (not met by the shipped code):** Full Moon times in 2026 within 1 hour of the almanac (the shipped mean-motion calendar is off by more than 5 hours on 3 January, 3 March and 28 August).

**Difficulty:** advanced

## Session 5: Moonrise for a real place

**You will learn:** How the Moon's own declination changes the rising time and why the delay is not always 50 minutes.

**You will build:** A moonrise calculator for a latitude, using the Moon's declination from the 5.145 degree tilt.

**Checkpoint (not met by the shipped code):** The delay between successive moonrises varies from night to night by at least 5 minutes at 40 N (the shipped equator model gives a constant 50.5 minutes).

**Difficulty:** intermediate

## Session 6: The analemma

**You will learn:** Why the Sun at the same clock time is not at the same place every day (the equation of time).

**You will build:** A figure-eight of the Sun's position at a fixed time through the year.

**Checkpoint (not met by the shipped code):** A curve whose height spans twice the tilt, 46.9 degrees, (not computed by the shipped code).

**Difficulty:** intermediate

## Session 7: Kepler orbit instead of a series

**You will learn:** Solving Kepler's equation for the Earth's position and speed.

**You will build:** An Earth-Sun distance and speed from the eccentricity 0.0167 by a numerical solver.

**Checkpoint (not met by the shipped code):** The ratio of the speeds at perihelion and aphelion is 1.034 (the shipped code does not compute speed).

**Difficulty:** advanced

## Session 8: Animate the whole sky

**You will learn:** Composing orbit, terminator, curves and phases in one animation.

**You will build:** A looping animation like the Target, with the Earth, the day-length curves and the Moon disc together.

**Checkpoint (not met by the shipped code):** A 48 frame loop whose first and last frames differ by less than 1e-6 in the data behind the picture.

**Difficulty:** advanced

## The final step

Combine the milestones: a looping animation of the tilted Earth on its orbit with the day-night line, the day-length curves for several latitudes and the Moon with updating phases, driven by calendar-accurate dates. If your result looks like the Target animation, open a pull request and tell us how you did it.
