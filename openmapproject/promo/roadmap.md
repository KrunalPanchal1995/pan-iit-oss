# Roadmap: the path to the openmapproject Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A compromise world map

**You will learn:** Why some world maps trade a little of every property, and how to score the trade-off.

**You will build:** A new projection function with a numerical Jacobian, plus a world picture with Tissot ellipses.

**Checkpoint (not met by the shipped code):** Over lat -75 to 75 and lon -180 to 180, area spread at most 3 and worst angle error at most 60 degrees (the shipped maps give at best 3.86 and 72 degrees for the equirectangular map, and 1.00 with 113 degrees for the sinusoidal map).

**Difficulty:** intermediate

## Session 5: A polar map

**You will learn:** Azimuthal projections centred on a pole, and why Mercator cannot draw it.

**You will build:** An azimuthal map with its own finite-difference distortion table.

**Checkpoint (not met by the shipped code):** Over lat 60 to 89 and all longitudes, worst angle error at most 3 degrees and area spread at most 1.1 (the shipped projections all fail one of these limits).

**Difficulty:** intermediate

## Session 6: A conformal conic map for a country

**You will learn:** How cone projections with two standard parallels keep angles and nearly keep areas in mid-latitudes.

**You will build:** A Lambert conformal conic function and a comparison with the four shipped maps.

**Checkpoint (not met by the shipped code):** For lat 8 to 37 and lon 68 to 97, worst angle error at most 0.001 degrees and area spread at most 1.10 (the shipped maps give 0.0 with spread 1.54 for Mercator, and spread 1.00 with 8.7 degrees for the sinusoidal map).

**Difficulty:** advanced

## Session 7: Routes across the dateline

**You will learn:** Great circles that cross +-180 degrees and how to draw them without jumps.

**You will build:** A route tool that draws great circles on three projections and reports lengths.

**Checkpoint (not met by the shipped code):** A route from Tokyo to Los Angeles drawn without a horizontal jump across the dateline, with its summed segment length within 0.01 percent of the haversine distance (the shipped point generator wraps at 180 degrees).

**Difficulty:** advanced

## Session 8: Unroll the globe

**You will learn:** Continuous families of maps that morph a sphere into a plane.

**You will build:** An animation of a globe unrolling into several maps with moving Tissot circles.

**Checkpoint (not met by the shipped code):** A GIF of at most 60 frames and 3 MB in which the numerical area scale at 40 degrees north changes by less than 0.15 between neighbouring frames.

**Difficulty:** advanced

## The final step

Combine the milestones: an unrolling globe with Tissot circles, a distortion table for any region, and an automatic recommendation of a projection with a one-line justification. If your result looks like the Target animation, open a pull request and tell us how you did it.
