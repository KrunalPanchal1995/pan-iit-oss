# Activity sheet: openemwave, Session 3: A wave simulator you can trust: FDTD

Name: ____________________   Date: ____________

**Objectives**

- Write a 1D and 2D FDTD simulation of Ez, Hx and Hy on a Yee grid in normalised units.
- Validate it: measure the wave speed, check energy conservation and see the Courant condition fail.
- Measure the 1/sqrt(r) fall-off of a 2D wave and the lambda / 2 spacing of standing-wave nodes.
- Find when the simulator is wrong (too few points per wavelength) and use two sources to make and steer a radiation pattern.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
You want to simulate a 2.4 GHz wifi wave in a 1 m square room with 20 cells per wavelength. Find the cell size, the largest stable time step in 2D, the number of steps per wave period and the number of cells across the room.

1. ______________________________  (hint: Wavelength: lambda = c / f = 2.998e8 / 2.4e9 = 0.1249 m....)
2. ______________________________  (hint: Cell size: dx = lambda / 20 = 0.1249 / 20 = 6.25 mm....)
3. ______________________________  (hint: Cells across 1 m: 1 / 0.006246 = 160 cells....)
4. ______________________________  (hint: Courant limit in 2D: dt <= dx / (c sqrt 2) = 6.246e-3 / (2.998e8 x 1.4...)
5. ______________________________  (hint: Period T = 1 / 2.4e9 = 416.7 ps, so the number of steps per period is ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a time step above the Courant limit make the simulation blow up, even though the true wave equation is perfectly well behaved? What does S mean physically?

Answer: ______________________________________________


**B. Numerical.** A grid has 8 points per wavelength and S = 0.5. Estimate the numerical phase speed as a fraction of c using 1 - (k dx)^2 (1 - S^2) / 24, and say whether the grid is good enough for a 1 percent accuracy.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the point-source amplitude measurement, the fitted slope on a log-log graph is -0.499. What does a slope of -0.5 mean, and what slope would a 3D source give? What would a slope of -1 in the 2D simulation tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose the phase difference between two sources a half wavelength apart so that the main beam points 45 degrees from their line, and say whether a spacing of 0.8 lambda is a good idea. Use the hand calculation, then say what you would check in the simulation.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
