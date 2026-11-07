# Roadmap: the path to the opensurvey Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Least-squares adjustment

**You will learn:** Weights, residuals and the normal equations, and why they use the information in the measurements better than a rule of thumb.

**You will build:** A second adjustment function that estimates the corner coordinates by weighted least squares and reports the residuals.

**Checkpoint (not met by the shipped code):** In the 4000-trial seeded Monte Carlo with the typical errors, the root-mean-square error of corner 5 is below 15 mm (the shipped Bowditch gives 16.3 mm).

**Difficulty:** intermediate

## Session 5: Find distance blunders too

**You will learn:** How a tape slip shows up in the misclosure, and how to tell it from an angle blunder.

**You will build:** A locator for the leg with a distance blunder, using the direction of the misclosure vector.

**Checkpoint (not met by the shipped code):** A 1 m slip on a random leg is assigned to the right leg in at least 95 percent of 500 seeded trials (the shipped locator handles angle blunders only; the misclosure of a distance slip lies along the bearing of its leg).

**Difficulty:** intermediate

## Session 6: A levelling network

**You will learn:** Several benchmarks joined by lines of levels, and sharing out loop misclosures by line length.

**You will build:** A loop of four levelling lines with known benchmark levels, adjusted so that every loop closes.

**Checkpoint (not met by the shipped code):** The adjusted loop closes to better than 1e-9 m and the line corrections are in proportion to the line lengths.

**Difficulty:** intermediate

## Session 7: Resection: where am I?

**You will learn:** Finding the position of a free station from angles to known points.

**You will build:** A function that solves the coordinates of an unknown station from the angles measured to three known points, with a picture of the geometry.

**Checkpoint (not met by the shipped code):** With error-free angles the station is recovered to within 1e-6 m; then report the RMS position error with 20 arc-second angles and explain which geometry is weak.

**Difficulty:** advanced

## Session 8: Contours and earthwork

**You will learn:** Turning spot heights into contour lines and a cut-and-fill volume for a building platform.

**You will build:** A grid of levels, contour lines, and the volume to cut and fill to make a level platform.

**Checkpoint (not met by the shipped code):** For a 60 m x 40 m plot with a 2 percent tilt levelled to its mean height, the cut volume is 360 m3 and equals the fill volume to within 1e-6 m3.

**Difficulty:** advanced

## The final step

Combine the milestones: a survey program that reduces a levelling network, adjusts a traverse by least squares, finds both kinds of blunder, and draws a contour map with the earthwork volume. If your result looks like the Target animation, open a pull request and tell us how you did it.
