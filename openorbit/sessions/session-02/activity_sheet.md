# Activity sheet: openorbit, Session 2: The mathematics of an orbit

Name: ____________________   Date: ____________

**Objectives**

- Find the semi-major axis and eccentricity from the perigee and apogee, and use the vis-viva equation for speed.
- Show that energy and angular momentum stay constant along an orbit.
- Solve Kepler's equation by Newton iteration and check the residual.
- Compare RK4 and a symplectic (leapfrog) integrator by measuring their energy error over many laps.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Design the orbit with perigee altitude 500 km and apogee altitude 35786 km. Find a, e, T, the speeds at perigee and apogee, and the satellite's distance one hour after perigee.

1. ______________________________  (hint: rp = 6371 + 500 = 6871 km and ra = 6371 + 35786 = 42157 km....)
2. ______________________________  (hint: a = (6871 + 42157) / 2 = 24514 km and e = (42157 - 6871) / (42157 + 68...)
3. ______________________________  (hint: T = 2 pi sqrt(a^3 / mu) = 10.610 hours....)
4. ______________________________  (hint: Vis-viva: perigee speed 9.988 km/s and apogee speed 1.628 km/s. Check ...)
5. ______________________________  (hint: Energy per kilogram = -mu / (2 a) = -8.13 MJ/kg at both ends....)
6. ______________________________  (hint: One hour after perigee: M = 2 pi * 3600 / (10.610 * 3600) = 0.5922 rad...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why must a satellite move faster at perigee than at apogee? Answer using both energy and angular momentum.

Answer: ______________________________________________


**B. Numerical.** Use Kepler's third law to find the period of an orbit with semi-major axis 24514 km. Check units and compare with the geostationary period.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the energy figure, which integrator would you trust for a simulation of 1000 laps, and why? Which is more accurate for 10 laps?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you need a 12 hour orbit that passes 500 km above the ground at perigee. What apogee altitude do you need, and what is the semi-major axis? How would you choose between this orbit and a circular one with the same period?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
