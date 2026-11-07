# Activity sheet: openorbit, Session 1: A satellite is falling around the Earth

Name: ____________________   Date: ____________

**Objectives**

- Explain why a satellite does not fall to the ground even though gravity pulls it.
- Compute the speed and period of a circular orbit at a given altitude, by hand and in Python.
- Explain why higher orbits are slower and take longer.
- State Kepler's three laws and read each as a picture.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the speed, period and gravity for a satellite 400 km above the ground, and check that the Earth curves away as fast as the satellite falls in one second.

1. ______________________________  (hint: Radius r = 6371 + 400 = 6771 km = 6.771e6 m....)
2. ______________________________  (hint: Gravity g = mu / r^2 = 3.986e14 / (6.771e6)^2 = 8.69 m/s^2 (compare 9....)
3. ______________________________  (hint: Speed v = sqrt(mu / r) = 7.67 km/s....)
4. ______________________________  (hint: Period T = 2 pi r / v = 2 pi * 6771 / 7.673 = 5545 s = 92.4 min....)
5. ______________________________  (hint: In 1 s the satellite falls 0.5 * 8.69 * 1^2 = 4.35 m. In 1 s it moves ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Astronauts on the station float. Is gravity switched off up there? Explain what 'weightless' means.

Answer: ______________________________________________


**B. Numerical.** Find the speed and period of a circular orbit 1000 km above the ground. Check the sanity of your answer against the 400 km orbit.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the speed and period graphs, what is the speed near 200 km and at the geostationary height, and what happens to the period? Why is the period curve steeper than the speed curve?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: an Earth-observation satellite should go round once every 100 minutes in a circular orbit. At what altitude should it fly and how fast does it move? Is the answer reasonable for a real satellite?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
