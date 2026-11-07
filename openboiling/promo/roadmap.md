# Roadmap: the path to the openboiling Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 5: A spherical bubble in the superheated liquid

**You will learn:** The heat equation in spherical coordinates with a moving boundary, and why curvature adds the factor sqrt(3).

**You will build:** A radial diffusion solver for the growing bubble.

**Checkpoint (not met by the shipped code):** Radius at 1 ms within 5 percent of the Plesset-Zwick value (the shipped planar solver gives 0.58 of it).

**Difficulty:** advanced

## Session 6: A plate with a temperature profile

**You will learn:** One-dimensional conduction through a thick plate and when the lumped model fails (Biot number).

**You will build:** A plate meshed in thickness with boiling as the boundary condition.

**Checkpoint (not met by the shipped code):** The temperature difference across a 20 mm copper plate matches q L / k within 1 percent at steady state (the shipped lumped plate has no gradient).

**Difficulty:** intermediate

## Session 7: From one bubble to a flux

**You will learn:** How site density, departure diameter and frequency combine into a boiling heat flux.

**You will build:** A bubble-ensemble model that predicts the nucleate flux.

**Checkpoint (not met by the shipped code):** The flux at 10 K superheat is within 30 percent of the Rohsenow-type value of 141 kW/m2 (the shipped illustrative curve gives 41 kW/m2).

**Difficulty:** advanced

## Session 8: Watch a bubble leave in 2D

**You will learn:** Interface tracking (volume of fluid or level set) for a rising bubble.

**You will build:** A two-dimensional simulation of a bubble growing, necking and departing.

**Checkpoint (not met by the shipped code):** Departure diameter within 20 percent of the Fritz value 2.34 mm at a 45 degree contact angle and vapour volume conserved to 0.1 percent.

**Difficulty:** advanced

## The final step

Combine the milestones: a boiling model with correlations at any pressure, a bubble that grows and departs, and a heater that shows burnout and hysteresis. If your result looks like the Target animation, open a pull request and tell us how you did it.
