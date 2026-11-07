# Activity sheet: openexoplanet, Session 2: The mathematics of a transit

Name: ____________________   Date: ____________

**Objectives**

- Compute the depth for Jupiter and for Earth around the Sun and see why Earth is so hard to find.
- Compute a transit light curve by numerical integration, with and without limb darkening, and check it against exact geometry.
- Predict the transit duration from the period and the impact parameter, using Kepler's third law.
- Solve a design problem: how quiet must a telescope be to see an Earth?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
An Earth twin crosses the centre of the Sun (b = 0) once per 365.25 days. Find its depth, a/Rs, the transit duration, and the noise per 30-minute measurement needed to detect it at SNR 7 from 3 transits.

1. ______________________________  (hint: k = 6371 / 695700 = 0.009158 and depth = k^2 = 8.39e-5 = 83.9 ppm....)
2. ______________________________  (hint: Kepler: a = (GM P^2 / 4 pi^2)^(1/3) = 1.496e11 m, which is 149.6 milli...)
3. ______________________________  (hint: T = (P/pi)(Rs/a) sqrt((1+k)^2) = (365.25/3.1416)(1/215.0)(1.00916) = 0...)
4. ______________________________  (hint: A 30-minute cadence gives floor(13.10 / 0.5) = 26 measurements per tra...)
5. ______________________________  (hint: sigma_max = depth x sqrt(n_in) / SNR = 83.9 ppm x sqrt(78) / 7 = 105.8...)
6. ______________________________  (hint: Check by simulation: the mean of 78 points with 105.8 ppm noise scatte...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the limb-darkened transit deeper in the middle than (Rp/Rs)^2, and why are its edges rounder?

Answer: ______________________________________________


**B. Numerical.** A planet with a radius of 2 Earth radii orbits a star of 0.5 solar radii. Find the transit depth in ppm.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the duration-against-b graph (k = 0.1, P = 3 d), read the duration at b = 0 and at b = 0.8. Why is it shorter at b = 0.8?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: your telescope gives 200 ppm noise per 30-minute point. How many transits of an Earth twin around a Sun-like star do you need for SNR 7? Is that practical?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
