# Activity sheet: openwatershed, Session 2: Two standard recipes: rational method and curve number

Name: ____________________   Date: ____________

**Objectives**

- Use the rational method Q = C i A / 3.6 and verify the factor 3.6 by hand.
- Compute run-off depth with the SCS curve number method and check its limits.
- Estimate a time of concentration and explain why the design storm lasts Tc.
- Solve a design problem for a made-up catchment: run-off depth, volume and peak.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Mango Creek (A = 4.5 km2) gets a 100 mm storm; CN = 80. Find S, Ia, the run-off depth and volume. Then estimate Tc, the design intensity and the rational peak with C = 0.45.

1. ______________________________  (hint: S = 25400/80 - 254 = 317.5 - 254 = 63.5 mm. Ia = 0.2 * 63.5 = 12.7 mm....)
2. ______________________________  (hint: P - Ia = 87.3 mm. Q = 87.3^2 / (87.3 + 63.5) = 7621.3 / 150.8 = 50.54 ...)
3. ______________________________  (hint: Volume = 0.05054 m * 4.5 km2 = 0.05054 * 4 500 000 m2 = about 227 thou...)
4. ______________________________  (hint: Slope = 64 / 3200 = 0.02. Tc = 0.0195 * 3200^0.77 * 0.02^-0.385 = 44.0...)
5. ______________________________  (hint: Intensity for a 44 min storm: i = 2000 / (44.0 + 15) = 33.9 mm/h (made...)
6. ______________________________  (hint: Rational peak = 0.45 * 33.9 * 4.5 / 3.6 = 19.1 m3/s....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the SCS curve give zero run-off for small storms, and why does Q stay below P for every storm?

Answer: ______________________________________________


**B. Numerical.** A 60 mm storm falls on Mango Creek with CN = 75. Find the run-off depth and the volume over 4.5 km2.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the run-off graph, at what storm depth does the CN 60 curve leave zero, and the CN 90 curve? What does the difference mean?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a plan straightens the channel of Mango Creek so that the slope doubles (0.02 to 0.04). Compute the new Tc and rational peak (C = 0.45, same area) and say whether the downstream culvert needs to be bigger. What do you assume?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
