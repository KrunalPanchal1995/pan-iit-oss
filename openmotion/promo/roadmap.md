# Roadmap: the path to the openmotion Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Fit the pieces, not the points

**You will learn:** How to recognise the corners of a trip and fit each constant-acceleration piece with its own formula.

**You will build:** A change-point fit of the three pieces of a noisy trip.

**Checkpoint (not met by the shipped code):** On the phone dataset the largest acceleration error stays below 0.5 m/s^2 (the shipped local fit stays above 1.5 m/s^2 for every window we tried).

**Difficulty:** intermediate

## Session 5: Let the data choose the window

**You will learn:** Cross-validation: judging a smoother by how well it predicts points it did not use.

**You will build:** A function that picks the smoothing window without knowing the true motion.

**Checkpoint (not met by the shipped code):** The chosen window gives an acceleration RMS error within 20 percent of the best fixed window on 20 noise seeds (the shipped code needs you to choose by hand).

**Difficulty:** advanced

## Session 6: Error bars on velocity

**You will learn:** How the noise of the data turns into an uncertainty of the estimate.

**You will build:** A 95 percent interval drawn around the recovered velocity.

**Checkpoint (not met by the shipped code):** Over 200 simulated noise seeds the interval contains the exact velocity at between 90 and 98 percent of the points (the shipped code gives no intervals).

**Difficulty:** advanced

## Session 7: Your own phone recording

**You will learn:** Getting positions out of a video, and judging the data you collected.

**You will build:** A recording of a rolling trolley analysed end to end.

**Checkpoint (not met by the shipped code):** Two recordings of the same run give cruise speeds within 0.05 m/s of each other, and within 3 percent of distance divided by stopwatch time.

**Difficulty:** intermediate

## Session 8: A tossed ball in two dimensions

**You will learn:** Motion graphs with two position coordinates, and acceleration as a vector.

**You will build:** The analysis of a ball toss filmed side-on.

**Checkpoint (not met by the shipped code):** The vertical acceleration is recovered as 9.8 m/s^2 within 0.3 m/s^2 and the horizontal acceleration is within 0.3 m/s^2 of zero (the shipped repo handles one dimension only).

**Difficulty:** advanced

## The final step

Combine the milestones: analyse a real phone recording of a moving body, draw the three graphs live with error bands, and report the velocity and acceleration with their uncertainty. If your result looks like the Target animation, open a pull request and tell us how you did it.
