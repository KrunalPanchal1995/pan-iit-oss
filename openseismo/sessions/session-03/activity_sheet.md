# Activity sheet: openseismo, Session 3: Real-world location: Geiger's method, pick errors and geometry

Name: ____________________   Date: ____________

**Objectives**

- Locate (x, y, t0) from P arrival times at N >= 4 stations with Geiger's Gauss-Newton method.
- Measure how pick noise and station geometry change the epicentre error (Monte Carlo, condition number).
- Draw and test a 95 percent error ellipse from the covariance.
- Explain why a constant-speed assumption biases the answer when the real speed rises with depth, and estimate a simple magnitude.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the surrounding network, quake (55, 40) km, vp = 6.0 km/s: compute the Jacobian row of station (5, 10) at the true quake, then describe the first Gauss-Newton step from the station centroid (50, 53).

1. ______________________________  (hint: Distance R = sqrt(50^2 + 30^2) = 58.31 km....)
2. ______________________________  (hint: Jx = -(5 - 55) / (6.0 x 58.31) = 50 / 349.9 = 0.143 s/km....)
3. ______________________________  (hint: Jy = -(10 - 40) / (6.0 x 58.31) = 30 / 349.9 = 0.086 s/km, and Jt0 = 1...)
4. ______________________________  (hint: The start (50, 53) is sqrt(5^2 + 13^2) = 13.9 km from the truth....)
5. ______________________________  (hint: One step with all five rows reduces that to 0.21 km, and the next step...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do stations all on one side of the quake give a much worse epicentre than stations all around it, even with the same pick errors?

Answer: ______________________________________________


**B. Numerical.** A station with S-P gap 20 s records a peak amplitude of 2 mm. Estimate ML with the approximate formula. Is it plausible? How does ML change for 20 mm?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the error-versus-sigma figure, what is the median error of the surrounding network at sigma = 0.2 s, and for the one-sided network? What does a straight line on the log plot tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you must report epicentres within about 1.5 km (95 percent) using picks with sigma = 0.1 s. Would the surrounding network meet this? What about the one-sided network, and what is the cheapest fix for it?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
